"""Case and CaseCriminal ORM models (Phase 5).

`Case` maps to the `cases` table; `CaseCriminal` maps to the `case_criminals`
junction table linking a case to criminal profiles (entities) with a role.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId


class CaseStatus(str, enum.Enum):
    """Values match the Postgres `case_status` enum."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class CasePriority(str, enum.Enum):
    """Values match the Postgres `case_priority` enum."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    # case_number is auto-generated from the DB id in the service (e.g. CASE-2026-0001),
    # so it is nullable at the ORM level but always populated before commit.
    case_number: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String(16), default=CaseStatus.OPEN.value, nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default=CasePriority.MEDIUM.value, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Case {self.case_number} title={self.title!r} status={self.status}>"


class CaseCriminal(Base):
    """Association between a Case and a CriminalProfile (role within the case)."""

    __tablename__ = "case_criminals"

    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True
    )
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("criminal_profiles.id", ondelete="CASCADE"), primary_key=True
    )
    role_in_case: Mapped[str | None] = mapped_column(String(64))
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
