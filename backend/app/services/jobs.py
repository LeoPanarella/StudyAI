"""Execução de trabalhos de IA em segundo plano.

Cada job abre sua própria sessão de banco (a sessão da requisição já foi fechada
quando o BackgroundTask roda). Toda transição de estado é persistida, então o
frontend pode acompanhar por polling e o estado sobrevive a recarregamentos.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import AIJob, Flashcard, Material, Summary
from app.services.ai.flashcards_generator import generate_flashcards_from_text
from app.services.ai.gemini import AIError
from app.services.ai.summarizer import summarize_material

log = logging.getLogger(__name__)

KIND_SUMMARY = "summary"
KIND_FLASHCARDS = "flashcards"

GENERIC_ERROR = "Ocorreu um erro inesperado ao gerar o conteúdo. Tente novamente."


def get_active_job(db: Session, material_id: int, kind: str) -> AIJob | None:
    return db.scalar(
        select(AIJob)
        .where(AIJob.material_id == material_id, AIJob.kind == kind, AIJob.status.in_(("pending", "running")))
        .order_by(AIJob.created_at.desc())
    )


def get_latest_job(db: Session, material_id: int, kind: str) -> AIJob | None:
    return db.scalar(
        select(AIJob)
        .where(AIJob.material_id == material_id, AIJob.kind == kind)
        .order_by(AIJob.created_at.desc(), AIJob.id.desc())
    )


def fail_stale_jobs() -> int:
    """Na inicialização: jobs que ficaram 'pending/running' pertencem a um processo que morreu."""
    with SessionLocal() as db:
        result = db.execute(
            update(AIJob)
            .where(AIJob.status.in_(("pending", "running")))
            .values(
                status="failed",
                error="A geração foi interrompida por um reinício do servidor. Tente novamente.",
                finished_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        if result.rowcount:
            log.warning("%d job(s) de IA marcados como falhos após reinício", result.rowcount)
        return result.rowcount


def run_job(job_id: int) -> None:
    """Ponto de entrada do BackgroundTask."""
    with SessionLocal() as db:
        job = db.get(AIJob, job_id)
        if job is None or job.status != "pending":
            return
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        job.attempts += 1
        db.commit()

        material = db.get(Material, job.material_id)
        if material is None:
            _finish(db, job, error="Material não encontrado.")
            return

        try:
            if job.kind == KIND_SUMMARY:
                model_used = _do_summary(db, material)
            elif job.kind == KIND_FLASHCARDS:
                model_used = _do_flashcards(db, material, focus=job.focus)
            else:
                raise ValueError(f"Tipo de job desconhecido: {job.kind}")
        except AIError as exc:
            log.warning("Job %d (%s) falhou: %s", job.id, job.kind, exc)
            _finish(db, job, error=str(exc))
            return
        except Exception:  # noqa: BLE001
            log.exception("Job %d (%s) falhou com erro inesperado", job.id, job.kind)
            _finish(db, job, error=GENERIC_ERROR)
            return

        _finish(db, job, model=model_used)
        log.info("Job %d (%s) concluído com %s", job.id, job.kind, model_used)


def _do_summary(db: Session, material: Material) -> str:
    text, model_used = summarize_material(material.title, material.content_text)
    summary = db.scalar(select(Summary).where(Summary.material_id == material.id))
    if summary is None:
        db.add(Summary(material_id=material.id, text=text, model=model_used))
    else:  # regenerar: substitui
        summary.text = text
        summary.model = model_used
        summary.generated_at = datetime.now(timezone.utc)
    db.commit()
    return model_used


def _do_flashcards(db: Session, material: Material, focus: str | None = None) -> str:
    cards_data, model_used = generate_flashcards_from_text(material.title, material.content_text, focus=focus)
    now = datetime.now(timezone.utc)
    for c in cards_data:
        db.add(
            Flashcard(
                material_id=material.id,
                question=c["question"],
                answer=c["answer"],
                repetitions=0,
                interval_days=0,
                ease_factor=2.5,
                next_review_at=now,
            )
        )
    db.commit()
    return model_used


def _finish(db: Session, job: AIJob, *, error: str | None = None, model: str | None = None) -> None:
    job.status = "failed" if error else "done"
    job.error = error
    job.model = model
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
