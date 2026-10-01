from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIJob(Base):
    """Trabalho de IA executado em segundo plano (resumo, flashcards...).

    O estado fica no banco para sobreviver a recarregamentos da página e permitir
    que o frontend acompanhe o progresso por polling.
    """

    __tablename__ = "ai_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)  # summary | flashcards
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending|running|done|failed
    error: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(100))  # modelo que concluiu o trabalho
    focus: Mapped[str | None] = mapped_column(String(500))  # foco temático opcional definido pelo aluno
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def is_active(self) -> bool:
        return self.status in ("pending", "running")
