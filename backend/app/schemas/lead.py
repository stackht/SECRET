"""Lead schemas (Phase 12)."""
from datetime import datetime

from pydantic import BaseModel, Field

LEAD_STATUSES = ("NEW", "REVIEWING", "CONFIRMED", "DISMISSED")


class LeadCreate(BaseModel):
    """Create an investigative lead from an analytical discovery."""

    kind: str = Field(default="POTENTIAL_LINK")
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: float = Field(default=0.0, ge=0, le=100)
    info_gain: float = Field(default=0.0, ge=0, le=100)
    entity_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    recommended_action: str | None = None
    recommended_source: str | None = None
    explanation: str | None = None


class LeadUpdate(BaseModel):
    """Update a lead (status, notes, review)."""

    status: str | None = Field(default=None, pattern="^(NEW|REVIEWING|CONFIRMED|DISMISSED)$")
    notes: str | None = None
    description: str | None = None


class LeadRead(BaseModel):
    id: int
    case_id: int
    kind: str
    title: str
    description: str | None = None
    priority: float
    info_gain: float
    status: str
    entity_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    recommended_action: str | None = None
    recommended_source: str | None = None
    explanation: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime