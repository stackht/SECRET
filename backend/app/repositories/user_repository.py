"""User data-access repository (Phase 3)."""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Async repository for the User model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_by(username=username)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_by(email=email)

    async def update_last_login(self, user: User, at: datetime) -> None:
        """Update the user's last_login_at and stage the change (flush)."""
        user.last_login_at = at
        self._session.add(user)
        await self._session.flush()
