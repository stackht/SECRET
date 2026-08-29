"""Seeding service (Phase 3).

Creates the default admin user for development/demonstration. Idempotent: it
skips creation when the user already exists.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


async def ensure_admin_user(session: AsyncSession) -> User | None:
    """Create the default admin if it does not exist. Returns the User or None.

    Credentials come from settings (dev defaults; override via .env in production).
    """
    settings = get_settings()

    repo = UserRepository(session)
    existing = await repo.get_by_username(settings.admin_username)
    if existing is not None:
        return existing

    admin = await repo.create(
        username=settings.admin_username,
        email=f"{settings.admin_username}@example.com",
        full_name="System Administrator",
        password_hash=hash_password(settings.admin_password),
        role=UserRole.ADMIN.value,
    )
    await session.commit()
    return admin
