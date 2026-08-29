"""Audit schemas (original Phase 13)."""
from datetime import datetime

from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    action: str = Field(min_length=1, max_length=128)
    object_type: str | None = Field(default=None, max_length=64)
    object_id: str | None = Field(default=None, max_length=64)
    result: dict = Field(default_factory=dict)


class AuditEntryRead(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    object_type: str | None = None
    object_id: str | None = None
    result: dict = Field(default_factory=dict)
    created_at: datetime
