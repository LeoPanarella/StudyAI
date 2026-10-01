from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MaterialConnection(Base):
    """Conexão associativa / grafo de conhecimento entre materiais (estilo Obsidian / Zettelkasten).

    Tipos de relação:
    - prerequisite: material de base/fundamento necessário
    - deepening: aprofundamento ou tópico avançado
    - related: conteúdo correlato ou análogo
    - application: aplicação prática ou estudo de caso
    """

    __tablename__ = "material_connections"
    __table_args__ = (
        UniqueConstraint("source_material_id", "target_material_id", name="uq_material_connection"),
        CheckConstraint("source_material_id != target_material_id", name="chk_connection_different"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"), index=True, nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(30), nullable=False, default="related")
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    source_material: Mapped["Material"] = relationship(  # noqa: F821
        "Material", foreign_keys=[source_material_id], back_populates="outgoing_connections"
    )
    target_material: Mapped["Material"] = relationship(  # noqa: F821
        "Material", foreign_keys=[target_material_id], back_populates="incoming_connections"
    )
