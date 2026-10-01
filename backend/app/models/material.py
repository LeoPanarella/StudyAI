from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # nome original do arquivo
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)  # caminho do PDF em disco
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_text: Mapped[str] = mapped_column(Text, nullable=False, default="")  # texto extraído
    char_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="materials")  # noqa: F821
    summary: Mapped["Summary | None"] = relationship(  # noqa: F821
        back_populates="material", cascade="all, delete-orphan", uselist=False
    )
    flashcards: Mapped[list["Flashcard"]] = relationship(  # noqa: F821
        back_populates="material", cascade="all, delete-orphan"
    )
    outgoing_connections: Mapped[list["MaterialConnection"]] = relationship(  # noqa: F821
        "MaterialConnection",
        foreign_keys="MaterialConnection.source_material_id",
        back_populates="source_material",
        cascade="all, delete-orphan",
    )
    incoming_connections: Mapped[list["MaterialConnection"]] = relationship(  # noqa: F821
        "MaterialConnection",
        foreign_keys="MaterialConnection.target_material_id",
        back_populates="target_material",
        cascade="all, delete-orphan",
    )
