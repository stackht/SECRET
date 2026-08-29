"""Security utilities: password hashing and JWT tokens.

Phase 3: full access + refresh token support.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# bcrypt via passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Refresh tokens live longer; access tokens are short-lived.
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain, hashed)


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": expire,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str,
    extra: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a short-lived access token."""
    expires = expires_delta or timedelta(minutes=get_settings().access_token_expire_minutes)
    return _create_token(subject, TOKEN_TYPE_ACCESS, expires, extra)


def create_refresh_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    """Create a longer-lived refresh token."""
    return _create_token(subject, TOKEN_TYPE_REFRESH, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), extra)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT, returning its claims."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
