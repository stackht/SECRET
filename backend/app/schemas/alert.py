"""Alert schemas (Phase 18)."""
from datetime import datetime

from pydantic import BaseModel, Field


class AlertRead(BaseModel):
    id: int
    case_id: int | None = None
    profile_id: int | None = None
    severity: str
    status: str
    title: str
    description: str | None = None
    score: float = 0.0
    confidence: float = 0.0
    source_ids: list[str] = Field(default_factory=list)
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    created_at: datetime


class AlertStatusUpdate(BaseModel):
    status: str = Field(pattern="^(NEW|REVIEWING|RESOLVED|DISMISSED)$")


class AlertGenerateResult(BaseModel):
    created: int
    alerts: list[AlertRead] = Field(default_factory=list)