"""User ORM model (Phase 3).

Maps to the `users` table. `role` and `status` are stored as VARCHAR so the
model works on both PostgreSQL (production) and SQLite (tests). Value integrity
is enforced at the API boundary via Pydantic schemas backed by the Python enums
`UserRole` / `UserStatus`.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_types import BigSerialId


class UserRole(str, enum.Enum):
    """Role values must match the PostgreSQL `user_role` enum (lowercase)."""

    ADMIN = "admin"
    ANALYST = "analyst"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """Values match the PostgreSQL `user_status` enum."""

    ACTIVE = "active"
    DISABLED = "disabled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigSerialId, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(32), default=UserRole.VIEWER.value, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=UserStatus.ACTIVE.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<User id={self.id} username={self.username!r} role={self.role}>"
