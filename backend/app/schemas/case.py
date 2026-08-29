"""Case schemas (Phase 5)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.case import CasePriority, CaseStatus
from app.schemas.criminal import CriminalProfileRead


class CaseCreate(BaseModel):
    """Input for creating a case."""

    title: str = Field(min_length=1, max_length=255)
    case_number: str | None = Field(default=None, max_length=64)
    description: str | None = None
    status: CaseStatus = CaseStatus.OPEN
    priority: CasePriority = CasePriority.MEDIUM


class CaseUpdate(BaseModel):
    """Optional partial update for a case."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: CaseStatus | None = None
    priority: CasePriority | None = None


class CaseRead(BaseModel):
    """Response payload for a case (list items)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    case_number: str
    title: str
    description: str | None = None
    status: CaseStatus
    priority: CasePriority
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None


class CaseList(BaseModel):
    """Paginated list response."""

    total: int
    limit: int
    offset: int
    items: list[CaseRead]


class CaseDetail(CaseRead):
    """Case detail including associated criminal profiles."""

    profiles: list[CriminalProfileRead] = Field(default_factory=list)


class CaseAssociateRequest(BaseModel):
    """Body to attach a criminal profile to a case."""

    profile_id: int
    role_in_case: str | None = Field(default=None, max_length=64)
