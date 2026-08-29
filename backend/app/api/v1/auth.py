"""Authentication endpoints (Phase 3)."""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive tokens",
)
async def login(payload: LoginRequest, session: DbSession) -> TokenResponse:
    """Validate credentials and return an access + refresh token pair."""
    service = AuthService(session)
    tokens = await service.login(payload.username, payload.password)
    await session.commit()
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an access token",
)
async def refresh(payload: RefreshRequest, session: DbSession) -> TokenResponse:
    """Exchange a valid refresh token for a fresh token pair."""
    service = AuthService(session)
    return await service.refresh(payload.refresh_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the authenticated user",
)
async def me(current_user: CurrentUser) -> User:
    """Return the currently authenticated user's profile."""
    return current_user
