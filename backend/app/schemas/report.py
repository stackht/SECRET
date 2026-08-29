"""Report schemas (Phase 9)."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReportType = Literal[
    "investigation_summary",
    "entity_intelligence",
    "network_analysis",
    "transaction_analysis",
    "communication_analysis",
]


class ReportRequest(BaseModel):
    """Request to generate a report."""

    report_type: ReportType
    case_number: str | None = Field(default=None, description="Case to base the report on")
    entity_id: str | None = Field(default=None, description="Entity for entity_intelligence")
    title: str | None = Field(default=None, max_length=255)


class ReportSection(BaseModel):
    """A single titled section within a report."""

    heading: str
    body: list[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    """A generated report: structured content plus a downloadable artifact."""

    id: str
    report_type: ReportType
    title: str
    generated_at: datetime
    generated_by: str
    sections: list[ReportSection] = Field(default_factory=list)
    artifact: str  # base64-encoded PDF preview (text-based, stdlib)
    artifact_mime: str = "application/pdf"


class ReportMeta(BaseModel):
    """Short metadata for a previously generated report."""

    id: str
    report_type: ReportType
    title: str
    generated_at: datetime
    generated_by: str
    sections: int
