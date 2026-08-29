"""Shared FastAPI dependencies (Phase 3).

Provides the DB session dependency and the `current_user` JWT guard.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.models.user import User, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPayload

# Security scheme: presents an "Authorize" button in Swagger.
bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: DbSession,
) -> User:
    """Resolve the authenticated user from the Bearer token.

    Raises 401 when the token is missing, malformed, not an access token, or
    the referenced user no longer exists.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
    except Exception:  # noqa: BLE001 - any JWT failure -> invalid credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = TokenPayload(**payload)
    try:
        user_id = int(token.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from None

    user = await UserRepository(session).get(user_id)
    if user is None or user.status == UserStatus.DISABLED.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer valid",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: str) -> User:
    """Build an `Annotated` role-guard alias for the given roles.

    The returned value is used as a FastAPI dependency (e.g.
    `_: RequireAnalyst`), enforcing that the current user holds any given role.
    Raises 403 otherwise.
    """
    def _guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )
        return user

    return Annotated[User, Depends(_guard)]


# Convenience guards reused across routers.
RequireAnalyst = require_roles("admin", "analyst")


def get_graph_store():
    """FastAPI dependency returning the graph store (Neo4j by default)."""
    from app.graph.store_factory import get_graph_store as _factory
    return _factory()


GraphStoreDep = Annotated[object, Depends(get_graph_store)]

