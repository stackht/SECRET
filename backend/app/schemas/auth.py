"""Authentication schemas (Phase 3)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole, UserStatus


class TokenPayload(BaseModel):
    """Decoded JWT payload extract."""

    sub: str
    role: str | None = None
    exp: int | None = None


class TokenResponse(BaseModel):
    """Access + refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login credentials."""

    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class RefreshRequest(BaseModel):
    """Refresh token payload."""

    refresh_token: str = Field(min_length=1)


class UserRead(BaseModel):
    """Public user representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login_at: datetime | None = None
