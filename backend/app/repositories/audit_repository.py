"""Audit log repository (original Phase 13)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Async repository for append-only audit entries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    async def list_recent(self, limit: int = 50) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
