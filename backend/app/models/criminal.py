"""CriminalProfile ORM model (Phase 4).

Maps to the `criminal_profiles` table. `aliases`/`attributes` use the shared
cross-dialect JSON type (JSONB on PostgreSQL, JSON on SQLite for tests). Enum-like
string fields are validated at the API boundary by Pydantic schemas.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId, JsonType


class EntityType(str, enum.Enum):
    """Entity types must match the Postgres `entity_type` enum AND the frontend
    types (src/types.ts): Person, Organization, Vehicle, Phone, Location, Account."""

    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    VEHICLE = "VEHICLE"
    PHONE = "PHONE"
    LOCATION = "LOCATION"
    ACCOUNT = "ACCOUNT"


class RiskLevel(str, enum.Enum):
    """Values match the Postgres `risk_level` enum."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CriminalProfile(Base):
    __tablename__ = "criminal_profiles"

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    # secret_id is derived from the assigned DB id in the create service, so it
    # is nullable at the ORM level (always populated before the transaction commits).
    secret_id: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    profile_type: Mapped[str] = mapped_column(String(16), nullable=False)  # EntityType
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list] = mapped_column(JsonType, default=list, nullable=False)
    risk_score: Mapped[float] = mapped_column(default=0.0, nullable=False)  # Numeric(5,2)
    risk_level: Mapped[str] = mapped_column(String(16), default=RiskLevel.LOW.value, nullable=False)
    confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)  # Numeric(5,2)
    status: Mapped[str] = mapped_column(String(32), default="MONITORED", nullable=False)
    attributes: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<CriminalProfile {self.secret_id} type={self.profile_type} name={self.name!r}>"
