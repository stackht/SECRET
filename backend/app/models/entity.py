"""Persisted canonical entities + relationships (Phase 2 ingestion).

Extracted entity mentions and relationship mentions are persisted per case so
the graph can be materialized from real, provenance-preserving relational rows
rather than only from manually curated criminal profiles.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId, JsonType


class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = (UniqueConstraint("case_id", "entity_id", "entity_type", name="uq_entity_case_type"),)

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)   # external id, e.g. N-4821
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)  # PERSON / PHONE / ...
    name: Mapped[str] = mapped_column(String(255), default="Unknown", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    attributes: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    source_ids: Mapped[list] = mapped_column(JsonType, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Entity {self.entity_id} type={self.entity_type} case={self.case_id}>"


class EntityRelationship(Base):
    __tablename__ = "entity_relationships"
    __table_args__ = (
        UniqueConstraint("case_id", "rel_type", "source_id", "target_id", name="uq_relationship_case"),
    )

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    rel_type: Mapped[str] = mapped_column(String(40), nullable=False)     # upper-cased, e.g. CALLED
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)   # external entity id
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_ids: Mapped[list] = mapped_column(JsonType, default=list, nullable=False)
    attributes: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Rel {self.source_id}-{self.rel_type}->{self.target_id} case={self.case_id}>"