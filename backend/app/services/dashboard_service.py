"""Dashboard summary (Command Center) computed from live database state."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.case import Case
from app.models.criminal import CriminalProfile
from app.models.entity import Entity, EntityRelationship
from app.models.source import Source

DEFAULT_ACTIVITY = {
    "cases": 0,
    "criminals": 0,
    "entities": 0,
    "relationships": 0,
    "sources": 0,
    "alerts": 0,
    "anomaly_signals": 0,
}


async def dashboard_summary(session: AsyncSession) -> dict:
    """Real counters + per-priority distribution. Never fabricates values."""
    async def _count(model) -> int:
        result = await session.execute(select(func.count()).select_from(model))
        return int(result.scalar_one())

    priorities = {}
    result = await session.execute(select(Case.priority, func.count()).group_by(Case.priority))
    priorities = {prio: int(n) for prio, n in result.all()}

    alerts_pending = await _count(Alert)
    return {
        **DEFAULT_ACTIVITY,
        "cases": await _count(Case),
        "criminals": await _count(CriminalProfile),
        "entities": await _count(Entity),
        "relationships": await _count(EntityRelationship),
        "sources": await _count(Source),
        "alerts": alerts_pending,
        "priority_distribution": priorities,
    }