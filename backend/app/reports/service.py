"""Report service (Phase 9).

Orchestrates report generation: invokes the appropriate builder from `BUILDERS`,
renders a PDF preview artifact, and stores the result in an in-memory store.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models.user import User
from app.reports.builders import BUILDERS
from app.reports.pdf import encode_pdf_artifact
from app.schemas.report import ReportMeta, ReportRequest, ReportResponse, ReportSection

# Simple in-memory store (reports survive only for the process lifetime).
_STORE: dict[str, ReportResponse] = {}


def _lines(sections: list[ReportSection]) -> list[str]:
    out: list[str] = []
    for section in sections:
        out.append("")
        out.append(f"## {section.heading}")
        out.extend(section.body)
    return out


class ReportService:
    """Generate and retrieve reports."""

    def __init__(self, session, store, user: User) -> None:
        self._session = session
        self._store = store
        self._user = user

    async def generate(self, request: ReportRequest) -> ReportResponse:
        builder = BUILDERS[request.report_type]

        if request.report_type == "investigation_summary":
            sections = await builder(self._session, self._store, request.case_number or "", request.title or "")
        elif request.report_type == "entity_intelligence":
            sections = await builder(self._session, self._store, request.entity_id or "", request.title or "")
        else:
            sections = await builder(self._session, self._store, request.title or "")

        title = request.title or request.report_type.replace("_", " ").title()
        artifact = encode_pdf_artifact(_lines(sections), title)

        report = ReportResponse(
            id=uuid.uuid4().hex,
            report_type=request.report_type,
            title=title,
            generated_at=datetime.now(timezone.utc),
            generated_by=self._user.username,
            sections=sections,
            artifact=artifact,
        )
        _STORE[report.id] = report
        return report

    def get_meta(self, report_id: str) -> ReportMeta | None:
        report = _STORE.get(report_id)
        if report is None:
            return None
        return ReportMeta(
            id=report.id,
            report_type=report.report_type,
            title=report.title,
            generated_at=report.generated_at,
            generated_by=report.generated_by,
            sections=len(report.sections),
        )

    def list_meta(self) -> list[ReportMeta]:
        return [self.get_meta(rid) for rid in _STORE if self.get_meta(rid) is not None]
