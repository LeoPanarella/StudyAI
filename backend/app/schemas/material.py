from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MaterialOut(BaseModel):
    """Item da lista — sem o texto completo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    filename: str
    file_size: int
    page_count: int
    char_count: int
    uploaded_at: datetime
    has_summary: bool = False
    flashcard_count: int = 0


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    text: str
    model: str | None
    generated_at: datetime


class AIJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    status: str  # pending | running | done | failed
    error: str | None
    focus: str | None = None
    created_at: datetime
    finished_at: datetime | None


class MaterialDetail(MaterialOut):
    """Detalhe — inclui prévia do texto extraído, o resumo, flashcards e jobs ativos."""

    content_preview: str
    extraction_warning: str | None = None
    summary: SummaryOut | None = None
    summary_job: AIJobOut | None = None
    flashcards_job: AIJobOut | None = None
    flashcards_due_count: int = 0


class MaterialContent(BaseModel):
    id: int
    content_text: str


class MaterialUpdate(BaseModel):
    title: str
