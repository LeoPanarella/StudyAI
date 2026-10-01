"""Endpoints de Flashcards e Revisão Espaçada (SM-2)."""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.rate_limit import ai_generation_limiter
from app.db.session import get_db
from app.models import AIJob, Flashcard, Material, User
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardListResponse,
    FlashcardOut,
    FlashcardReview,
    FlashcardsGenerateRequest,
    FlashcardUpdate,
)
from app.schemas.material import AIJobOut
from app.services import jobs
from app.services.spaced_repetition import apply_sm2

router = APIRouter(tags=["flashcards"])


def _get_owned_material(material_id: int, user: User, db: Session) -> Material:
    material = db.get(Material, material_id)
    if material is None or material.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado.")
    return material


def _get_owned_flashcard(flashcard_id: int, user: User, db: Session) -> tuple[Flashcard, Material]:
    card = db.get(Flashcard, flashcard_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard não encontrado.")
    material = db.get(Material, card.material_id)
    if material is None or material.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard não encontrado.")
    return card, material


def _card_to_out(card: Flashcard, now: datetime) -> FlashcardOut:
    out = FlashcardOut.model_validate(card)
    out.is_due = card.next_review_at is None or card.next_review_at <= now
    return out


# ---------- Listagem e Criação por Material ----------

@router.get("/materials/{material_id}/flashcards", response_model=FlashcardListResponse)
def list_flashcards(
    material_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_material(material_id, user, db)
    now = datetime.now(timezone.utc)
    cards = db.scalars(
        select(Flashcard)
        .where(Flashcard.material_id == material_id)
        .order_by(Flashcard.id.asc())
    ).all()

    due_count = sum(1 for c in cards if c.next_review_at is None or c.next_review_at <= now)
    items = [_card_to_out(c, now) for c in cards]
    return FlashcardListResponse(items=items, total_count=len(cards), due_count=due_count)


@router.post(
    "/materials/{material_id}/flashcards",
    response_model=FlashcardOut,
    status_code=status.HTTP_201_CREATED,
)
def create_manual_flashcard(
    material_id: int,
    payload: FlashcardCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = _get_owned_material(material_id, user, db)
    now = datetime.now(timezone.utc)
    card = Flashcard(
        material_id=material.id,
        question=payload.question,
        answer=payload.answer,
        repetitions=0,
        interval_days=0,
        ease_factor=2.5,
        next_review_at=now,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return _card_to_out(card, now)


@router.post(
    "/materials/{material_id}/flashcards/generate",
    response_model=AIJobOut,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(ai_generation_limiter)],
)
def generate_flashcards(
    material_id: int,
    background: BackgroundTasks,
    payload: FlashcardsGenerateRequest | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enfileira geração de flashcards via IA em segundo plano, opcionalmente com foco temático."""
    material = _get_owned_material(material_id, user, db)
    if material.char_count == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este material não contém texto extraível para gerar flashcards.",
        )

    active = jobs.get_active_job(db, material.id, jobs.KIND_FLASHCARDS)
    if active is not None:
        return active

    focus_text = payload.focus.strip() if payload and payload.focus else None
    job = AIJob(
        material_id=material.id,
        kind=jobs.KIND_FLASHCARDS,
        status="pending",
        focus=focus_text,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    background.add_task(jobs.run_job, job.id)
    return job


# ---------- Sessão de Estudo / Revisão ----------

@router.get("/materials/{material_id}/flashcards/study", response_model=list[FlashcardOut])
def get_study_cards(
    material_id: int,
    mode: str = Query(default="all", enum=["due", "all"]),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna os cartões para a sessão de revisão.

    mode=due: retorna apenas os que venceram a data de revisão;
    mode=all: retorna todos os cartões do material (priorizando os vencidos primeiro).
    """
    _get_owned_material(material_id, user, db)
    now = datetime.now(timezone.utc)

    query = select(Flashcard).where(Flashcard.material_id == material_id)
    if mode == "due":
        query = query.where((Flashcard.next_review_at.is_(None)) | (Flashcard.next_review_at <= now))

    # Prioriza os que estão para vencer ou nunca foram revisados
    query = query.order_by(Flashcard.next_review_at.asc().nullsfirst(), Flashcard.id.asc())
    cards = db.scalars(query).all()
    return [_card_to_out(c, now) for c in cards]


@router.post("/flashcards/{flashcard_id}/review", response_model=FlashcardOut)
def review_flashcard(
    flashcard_id: int,
    payload: FlashcardReview,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submete uma resposta de revisão (0=Errei, 1=Difícil, 2=Bom, 3=Fácil) e atualiza o SM-2."""
    card, _ = _get_owned_flashcard(flashcard_id, user, db)

    reps, interval, ef, next_review, now = apply_sm2(
        repetitions=card.repetitions,
        interval_days=card.interval_days,
        ease_factor=card.ease_factor,
        rating=payload.rating,
    )

    card.repetitions = reps
    card.interval_days = interval
    card.ease_factor = ef
    card.next_review_at = next_review
    card.last_reviewed_at = now

    db.commit()
    db.refresh(card)
    return _card_to_out(card, now)


# ---------- Edição e Exclusão Individual ----------

@router.patch("/flashcards/{flashcard_id}", response_model=FlashcardOut)
def update_flashcard(
    flashcard_id: int,
    payload: FlashcardUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    card, _ = _get_owned_flashcard(flashcard_id, user, db)
    if payload.question is not None:
        card.question = payload.question
    if payload.answer is not None:
        card.answer = payload.answer

    db.commit()
    db.refresh(card)
    now = datetime.now(timezone.utc)
    return _card_to_out(card, now)


@router.delete("/flashcards/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(
    flashcard_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    card, _ = _get_owned_flashcard(flashcard_id, user, db)
    db.delete(card)
    db.commit()
