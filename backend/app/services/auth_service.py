"""Authentication service (Phase 3).

Business logic for login, token issuance/refresh, and current-user resolution.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    """Coordinates authentication flows against the user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    def _issue_tokens(self, user: User) -> TokenResponse:
        """Build a token pair for a user (subject = user id)."""
        extra = {"username": user.username, "role": user.role}
        access = create_access_token(str(user.id), extra=extra)
        refresh = create_refresh_token(str(user.id), extra=extra)
        return TokenResponse(access_token=access, refresh_token=refresh)

    async def authenticate(self, username: str, password: str) -> User:
        """Validate credentials. Raise 401 on failure or on disabled users."""
        user = await self._repo.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if user.status == UserStatus.DISABLED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )
        return user

    async def login(self, username: str, password: str) -> TokenResponse:
        """Authenticate and return a fresh token pair."""
        user = await self.authenticate(username, password)
        await self._repo.update_last_login(user, datetime.now(timezone.utc))
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Validate a refresh token and issue a new token pair."""
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:  # noqa: BLE001 - any JWT error -> invalid refresh
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from exc

        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not a refresh token",
            )

        user = await self._repo.get(int(payload["sub"]))
        if user is None or user.status == UserStatus.DISABLED.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer valid",
            )
        return self._issue_tokens(user)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._repo.get(user_id)


def require_admin(user: User) -> None:
    """Enforce admin role; used by protected admin endpoints."""
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
