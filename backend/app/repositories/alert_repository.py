"""Alert repository (Phase 18)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Async repository for alerts."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Alert)

    async def list_by_case(self, case_id: int, limit: int = 100) -> list[Alert]:
        stmt = (
            select(Alert)
            .where(Alert.case_id == case_id)
            .order_by(Alert.created_at.desc(), Alert.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self, limit: int = 100) -> list[Alert]:
        stmt = select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())