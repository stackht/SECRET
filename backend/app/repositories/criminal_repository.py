"""Criminal profile data-access repository (Phase 4)."""
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.criminal import CriminalProfile
from app.repositories.base import BaseRepository


@dataclass
class ProfileFilters:
    """Optional filters applied when listing profiles."""

    q: str | None = None            # free-text search on name/secret_id/aliases
    profile_type: str | None = None
    risk_level: str | None = None
    status: str | None = None


class CriminalRepository(BaseRepository[CriminalProfile]):
    """Async repository for CriminalProfile records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CriminalProfile)

    async def get_by_secret_id(self, secret_id: str) -> CriminalProfile | None:
        return await self.get_by(secret_id=secret_id)

    def _apply_filters(self, stmt, filters: ProfileFilters):
        if filters.q:
            like = f"%{filters.q}%"
            stmt = stmt.where(
                or_(
                    CriminalProfile.name.ilike(like),
                    CriminalProfile.secret_id.ilike(like),
                )
            )
        if filters.profile_type:
            stmt = stmt.where(CriminalProfile.profile_type == filters.profile_type)
        if filters.risk_level:
            stmt = stmt.where(CriminalProfile.risk_level == filters.risk_level)
        if filters.status:
            stmt = stmt.where(CriminalProfile.status == filters.status)
        return stmt

    async def list_profiles(
        self,
        filters: ProfileFilters,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CriminalProfile]:
        stmt = select(CriminalProfile).order_by(CriminalProfile.id)
        stmt = self._apply_filters(stmt, filters).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_profiles(self, filters: ProfileFilters) -> int:
        stmt = select(func.count(CriminalProfile.id))
        stmt = self._apply_filters(stmt, filters)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
