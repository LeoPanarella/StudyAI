from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FlashcardBase(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    answer: str = Field(min_length=1, max_length=2000)

    @field_validator("question", "answer")
    @classmethod
    def strip_text(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("O campo não pode ser vazio.")
        return s


class FlashcardCreate(FlashcardBase):
    pass


class FlashcardUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=2, max_length=1000)
    answer: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("question", "answer")
    @classmethod
    def strip_text(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("O campo não pode ser vazio.")
        return s


class FlashcardReview(BaseModel):
    # 0 = Errei, 1 = Difícil, 2 = Bom, 3 = Fácil
    rating: int = Field(ge=0, le=3)


class FlashcardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    question: str
    answer: str
    created_at: datetime
    repetitions: int
    interval_days: int
    ease_factor: float
    next_review_at: datetime | None
    last_reviewed_at: datetime | None
    is_due: bool = False


class FlashcardListResponse(BaseModel):
    items: list[FlashcardOut]
    total_count: int
    due_count: int


class FlashcardsGenerateRequest(BaseModel):
    focus: str | None = None
