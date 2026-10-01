"""Endpoints para Conexões e Grafo Associativo entre Materiais (estilo Obsidian)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Material, MaterialConnection, User
from app.schemas.connection import (
    AvailableTarget,
    BacklinkOut,
    ConnectionCreate,
    ConnectionOut,
    MaterialConnectionsResponse,
)

router = APIRouter(tags=["connections"])


def _get_owned_material(material_id: int, user: User, db: Session) -> Material:
    material = db.get(Material, material_id)
    if material is None or material.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado.")
    return material


@router.get("/materials/{material_id}/connections", response_model=MaterialConnectionsResponse)
def get_material_connections(
    material_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = _get_owned_material(material_id, user, db)

    # 1. Conexões de saída (materiais aos quais este se conecta: ex. "este material requer X")
    outgoing_conns = db.scalars(
        select(MaterialConnection)
        .where(MaterialConnection.source_material_id == material.id)
        .order_by(MaterialConnection.created_at.desc())
    ).all()

    outgoing_items = []
    for c in outgoing_conns:
        target = db.get(Material, c.target_material_id)
        if target:
            outgoing_items.append(
                ConnectionOut(
                    id=c.id,
                    source_material_id=c.source_material_id,
                    target_material_id=c.target_material_id,
                    target_material_title=target.title,
                    target_material_filename=target.filename,
                    relation_type=c.relation_type,
                    note=c.note,
                    created_at=c.created_at,
                )
            )

    # 2. Conexões de entrada / Backlinks (outros materiais que apontam para este)
    incoming_conns = db.scalars(
        select(MaterialConnection)
        .where(MaterialConnection.target_material_id == material.id)
        .order_by(MaterialConnection.created_at.desc())
    ).all()

    incoming_items = []
    for c in incoming_conns:
        source = db.get(Material, c.source_material_id)
        if source:
            incoming_items.append(
                BacklinkOut(
                    id=c.id,
                    source_material_id=c.source_material_id,
                    source_material_title=source.title,
                    source_material_filename=source.filename,
                    relation_type=c.relation_type,
                    note=c.note,
                    created_at=c.created_at,
                )
            )

    # 3. Lista de outros materiais do usuário elegíveis para nova conexão
    other_materials = db.scalars(
        select(Material)
        .where(Material.user_id == user.id, Material.id != material.id)
        .order_by(Material.uploaded_at.desc())
    ).all()

    available = [AvailableTarget(id=m.id, title=m.title, filename=m.filename) for m in other_materials]

    return MaterialConnectionsResponse(
        outgoing=outgoing_items,
        incoming=incoming_items,
        available_targets=available,
    )


@router.post(
    "/materials/{material_id}/connections",
    response_model=ConnectionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_connection(
    material_id: int,
    payload: ConnectionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = _get_owned_material(material_id, user, db)

    if payload.target_material_id == source.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível conectar um material a si mesmo.",
        )

    target = _get_owned_material(payload.target_material_id, user, db)

    # Verifica se já existe a conexão
    existing = db.scalar(
        select(MaterialConnection).where(
            MaterialConnection.source_material_id == source.id,
            MaterialConnection.target_material_id == target.id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta conexão já existe entre os dois materiais.",
        )

    valid_types = {"prerequisite", "deepening", "related", "application"}
    rel_type = payload.relation_type if payload.relation_type in valid_types else "related"

    conn = MaterialConnection(
        source_material_id=source.id,
        target_material_id=target.id,
        relation_type=rel_type,
        note=payload.note.strip() if payload.note else None,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)

    return ConnectionOut(
        id=conn.id,
        source_material_id=conn.source_material_id,
        target_material_id=conn.target_material_id,
        target_material_title=target.title,
        target_material_filename=target.filename,
        relation_type=conn.relation_type,
        note=conn.note,
        created_at=conn.created_at,
    )


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conn = db.get(MaterialConnection, connection_id)
    if conn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conexão não encontrada.")

    # O usuário precisa ser dono do material de origem ou de destino
    source = db.get(Material, conn.source_material_id)
    if source is None or source.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conexão não encontrada.")

    db.delete(conn)
    db.commit()
