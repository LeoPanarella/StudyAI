import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import ai_generation_limiter
from app.db.session import get_db
from app.models import AIJob, Flashcard, Material, Summary, User
from app.schemas.material import AIJobOut, MaterialContent, MaterialDetail, MaterialOut, MaterialUpdate, SummaryOut
from app.services import jobs
from app.services.pdf_extractor import PdfExtractionError, extract_text

router = APIRouter(prefix="/materials", tags=["materials"])

PREVIEW_CHARS = 2500


# ---------- helpers ----------

def _title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"[_\-]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return (stem or "Material sem título")[:200]


def _get_owned_material(material_id: int, user: User, db: Session) -> Material:
    material = db.get(Material, material_id)
    if material is None or material.user_id != user.id:
        # 404 também para materiais de outros usuários: não revelamos a existência.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado.")
    return material


def _to_out(material: Material, has_summary: bool, flashcard_count: int) -> MaterialOut:
    return MaterialOut(
        id=material.id,
        title=material.title,
        filename=material.filename,
        file_size=material.file_size,
        page_count=material.page_count,
        char_count=material.char_count,
        uploaded_at=material.uploaded_at,
        has_summary=has_summary,
        flashcard_count=flashcard_count,
    )


def _to_detail(material: Material, db: Session, warning: str | None = None) -> MaterialDetail:
    now = datetime.now(timezone.utc)
    summary = db.scalar(select(Summary).where(Summary.material_id == material.id))
    flashcard_count = db.scalar(select(func.count(Flashcard.id)).where(Flashcard.material_id == material.id)) or 0
    due_count = (
        db.scalar(
            select(func.count(Flashcard.id)).where(
                Flashcard.material_id == material.id,
                (Flashcard.next_review_at.is_(None)) | (Flashcard.next_review_at <= now),
            )
        )
        or 0
    )
    base = _to_out(material, summary is not None, flashcard_count)
    if warning is None and material.char_count == 0:
        warning = "Nenhum texto foi encontrado neste PDF (documento escaneado?)."
    summary_job = jobs.get_latest_job(db, material.id, jobs.KIND_SUMMARY)
    flashcards_job = jobs.get_latest_job(db, material.id, jobs.KIND_FLASHCARDS)
    return MaterialDetail(
        **base.model_dump(),
        content_preview=material.content_text[:PREVIEW_CHARS],
        extraction_warning=warning,
        summary=SummaryOut.model_validate(summary) if summary else None,
        summary_job=AIJobOut.model_validate(summary_job) if summary_job else None,
        flashcards_job=AIJobOut.model_validate(flashcards_job) if flashcards_job else None,
        flashcards_due_count=due_count,
    )


async def _read_upload_limited(file: UploadFile, limit: int) -> bytes:
    """Lê o upload em blocos e aborta cedo se ultrapassar o limite (evita estourar memória)."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"O arquivo excede o limite de {settings.MAX_UPLOAD_MB} MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


# ---------- rotas ----------

@router.get("", response_model=list[MaterialOut])
def list_materials(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary_exists = (
        select(func.count(Summary.id)).where(Summary.material_id == Material.id).scalar_subquery()
    )
    flashcards_count = (
        select(func.count(Flashcard.id)).where(Flashcard.material_id == Material.id).scalar_subquery()
    )
    rows = db.execute(
        select(Material, summary_exists, flashcards_count)
        .where(Material.user_id == user.id)
        .order_by(Material.uploaded_at.desc())
    ).all()
    return [_to_out(m, bool(s), fc) for m, s, fc in rows]


@router.post("", response_model=MaterialDetail, status_code=status.HTTP_201_CREATED)
async def upload_material(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    original_name = (file.filename or "arquivo.pdf").strip()
    if not original_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie um arquivo PDF (.pdf).")

    data = await _read_upload_limited(file, settings.max_upload_bytes)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O arquivo está vazio.")

    # Validação de magic bytes para garantir que é um PDF real
    if not data.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado não possui assinatura binária de um documento PDF válido.",
        )

    try:
        extracted = extract_text(data)
    except PdfExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # Guarda o PDF original em disco: uploads/<user_id>/<uuid>.pdf
    user_dir = settings.UPLOAD_DIR / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_path = user_dir / f"{uuid.uuid4().hex}.pdf"
    stored_path.write_bytes(data)

    material = Material(
        user_id=user.id,
        title=(title or "").strip()[:200] or _title_from_filename(original_name),
        filename=original_name[:255],
        stored_path=str(stored_path),
        file_size=len(data),
        page_count=extracted.page_count,
        content_text=extracted.text,
        char_count=extracted.char_count,
    )
    db.add(material)
    try:
        db.commit()
    except Exception:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise
    db.refresh(material)
    return _to_detail(material, db, warning=extracted.warning)


@router.get("/{material_id}", response_model=MaterialDetail)
def get_material(material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    material = _get_owned_material(material_id, user, db)
    return _to_detail(material, db)


@router.get("/{material_id}/content", response_model=MaterialContent)
def get_material_content(
    material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    material = _get_owned_material(material_id, user, db)
    return MaterialContent(id=material.id, content_text=material.content_text)


# ---------- resumo (IA) ----------

@router.get("/{material_id}/summary", response_model=SummaryOut)
def get_summary(material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    material = _get_owned_material(material_id, user, db)
    summary = db.scalar(select(Summary).where(Summary.material_id == material.id))
    if summary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Este material ainda não tem resumo.")
    return summary


@router.post("/{material_id}/summary", response_model=AIJobOut, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(ai_generation_limiter)])
def generate_summary(
    material_id: int,
    background: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enfileira a geração (ou regeneração) do resumo. Acompanhe pelo campo `summary_job`
    do detalhe do material; quando `status` for `done`, o `summary` estará preenchido."""
    material = _get_owned_material(material_id, user, db)
    if material.char_count == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este material não tem texto extraível, então não é possível gerar um resumo.",
        )

    # Já existe geração em andamento? Devolve o job atual em vez de duplicar trabalho.
    active = jobs.get_active_job(db, material.id, jobs.KIND_SUMMARY)
    if active is not None:
        return active

    job = AIJob(material_id=material.id, kind=jobs.KIND_SUMMARY, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    background.add_task(jobs.run_job, job.id)
    return job


@router.patch("/{material_id}", response_model=MaterialDetail)
def update_material(
    material_id: int,
    payload: MaterialUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = _get_owned_material(material_id, user, db)
    new_title = payload.title.strip()[:200]
    if not new_title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O título não pode ficar vazio.")
    material.title = new_title
    db.commit()
    db.refresh(material)
    return _to_detail(material, db)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    material = _get_owned_material(material_id, user, db)
    path = Path(material.stored_path)
    db.delete(material)  # resumo e flashcards caem em cascata
    db.commit()
    path.unlink(missing_ok=True)
