"""Criminal profile schemas (Phase 4)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.criminal import EntityType, RiskLevel


class CriminalProfileCreate(BaseModel):
    """Input for creating a criminal/entity profile."""

    profile_type: EntityType
    name: str = Field(min_length=1, max_length=255)
    aliases: list[str] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0, le=100)
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float = Field(default=0.0, ge=0, le=100)
    status: str = Field(default="MONITORED", max_length=32)
    attributes: dict = Field(default_factory=dict)

    @field_validator("attributes")
    @classmethod
    def _attributes_type_safe(cls, v: dict) -> dict:
        return v if isinstance(v, dict) else {}


class CriminalProfileUpdate(BaseModel):
    """Optional partial update for a profile."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    aliases: list[str] | None = None
    risk_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    confidence: float | None = Field(default=None, ge=0, le=100)
    status: str | None = Field(default=None, max_length=32)
    attributes: dict | None = None


class CriminalProfileRead(BaseModel):
    """Response payload for a single profile."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    secret_id: str
    profile_type: EntityType
    name: str
    aliases: list[str]
    risk_score: float
    risk_level: RiskLevel
    confidence: float
    status: str
    attributes: dict
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime | None = None


class CriminalProfileList(BaseModel):
    """Paginated list response."""

    total: int
    limit: int
    offset: int
    items: list[CriminalProfileRead]
