"""Case data source ORM model (Phase 2-3).

Persistent source registry: every uploaded/ingested dataset tied to a case.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId, JsonType


class Source(Base):
    __tablename__ = "case_sources"

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(32))      # csv/json/txt/...
    source_type: Mapped[str | None] = mapped_column(String(32))    # CDR/FIR/TRANSACTION/...
    status: Mapped[str] = mapped_column(String(24), default="UPLOADED", nullable=False)
    record_count: Mapped[int | None] = mapped_column(Integer)
    processing_error: Mapped[str | None] = mapped_column(String(512))
    metadata_json: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Source {self.source_id} case={self.case_id} status={self.status}>"
