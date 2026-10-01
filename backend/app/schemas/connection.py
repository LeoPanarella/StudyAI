from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConnectionCreate(BaseModel):
    target_material_id: int
    relation_type: str = Field(default="related")  # prerequisite | deepening | related | application
    note: str | None = Field(default=None, max_length=500)


class ConnectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_material_id: int
    target_material_id: int
    target_material_title: str
    target_material_filename: str
    relation_type: str
    note: str | None
    created_at: datetime


class BacklinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_material_id: int
    source_material_title: str
    source_material_filename: str
    relation_type: str
    note: str | None
    created_at: datetime


class AvailableTarget(BaseModel):
    id: int
    title: str
    filename: str


class MaterialConnectionsResponse(BaseModel):
    outgoing: list[ConnectionOut]
    incoming: list[BacklinkOut]
    available_targets: list[AvailableTarget]
