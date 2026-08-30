"""Source repository (Phase 2-3)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.repositories.base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """Async repository for case data sources."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Source)

    async def list_by_case(self, case_id: int) -> list[Source]:
        stmt = select(Source).where(Source.case_id == case_id).order_by(Source.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_case_and_source(self, case_id: int, source_id: str) -> Source | None:
        stmt = (
            select(Source)
            .where(Source.case_id == case_id, Source.source_id == source_id)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()