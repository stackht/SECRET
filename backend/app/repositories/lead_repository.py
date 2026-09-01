"""Investigative lead repository (Phase 12)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """Async repository for investigative leads."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Lead)

    async def list_by_case(self, case_id: int, limit: int = 100) -> list[Lead]:
        stmt = (
            select(Lead)
            .where(Lead.case_id == case_id)
            .order_by(Lead.priority.desc(), Lead.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())