"""Alert ORM model (Phase 18).

Maps to the `alerts` table (Phase 1 schema). Column-based (SQLite-compatible
enum-ish strings; PostgreSQL enum cast paths follow the pattern set by
`criminal_profiles` / `cases`).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId, JsonType


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("criminal_profiles.id", ondelete="SET NULL"))
    severity: Mapped[str] = mapped_column(String(16), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="NEW", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_ids: Mapped[list] = mapped_column(JsonType, default=list, nullable=False)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Alert {self.id} {self.severity} {self.title!r} case={self.case_id}>"