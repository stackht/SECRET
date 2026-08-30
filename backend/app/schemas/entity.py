"""Persisted entity + relationship read schemas (Phase 2)."""
from datetime import datetime

from pydantic import BaseModel, Field


class EntityRead(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    confidence: float
    attributes: dict = Field(default_factory=dict)
    source_ids: list[str] = Field(default_factory=list)
    created_at: datetime


class RelationshipRead(BaseModel):
    rel_type: str
    source_id: str
    target_id: str
    confidence: float
    source_ids: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    created_at: datetime