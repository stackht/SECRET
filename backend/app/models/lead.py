"""Investigative lead ORM model (Phase 12).

A lead is an INVESTIGATIVE HYPOTHESIS derived from analytical discoveries
(potential link, anomaly, evidence gap, priority action). Never a guilt finding.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId, JsonType


class Lead(Base):
    __tablename__ = "investigative_leads"

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(40), default="POTENTIAL_LINK", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    info_gain: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="NEW", nullable=False)
    entity_ids: Mapped[list] = mapped_column(JsonType, default=list, nullable=False)
    evidence_ids: Mapped[list] = mapped_column(JsonType, default=list, nullable=False)
    recommended_action: Mapped[str | None] = mapped_column(Text)
    recommended_source: Mapped[str | None] = mapped_column(String(64))
    explanation: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Lead {self.id} {self.kind} {self.title!r} status={self.status}>"