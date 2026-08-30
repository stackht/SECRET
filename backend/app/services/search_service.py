"""Global case search (Phase 21).

Search across persisted cases, criminal profiles, ingested entities, and source
registries by free-text query.
"""
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.criminal import CriminalProfile
from app.models.entity import Entity
from app.models.source import Source


async def global_search(session: AsyncSession, q: str, limit: int = 10) -> dict:
    """Return typed result groups for a query string."""
    term = (q or "").strip()
    if not term:
        return {"query": term, "cases": [], "criminals": [], "entities": [], "sources": []}
    pattern = f"%{term}%"

    cases = list(
        (await session.execute(
            select(Case.case_number, Case.title, Case.status)
            .where(or_(Case.case_number.ilike(pattern), Case.title.ilike(pattern)))
            .limit(limit)
        )).all()
    )
    criminals = list(
        (await session.execute(
            select(CriminalProfile.secret_id, CriminalProfile.name, CriminalProfile.profile_type, CriminalProfile.risk_level)
            .where(or_(CriminalProfile.name.ilike(pattern), CriminalProfile.secret_id.ilike(pattern)))
            .limit(limit)
        )).all()
    )
    entities = list(
        (await session.execute(
            select(Entity.entity_id, Entity.entity_type, Entity.name, Entity.case_id)
            .where(or_(Entity.entity_id.ilike(pattern), Entity.name.ilike(pattern)))
            .limit(limit)
        )).all()
    )
    sources = list(
        (await session.execute(
            select(Source.source_id, Source.filename, Source.source_type, Source.case_id, Source.status)
            .where(or_(Source.source_id.ilike(pattern), Source.filename.ilike(pattern)))
            .limit(limit)
        )).all()
    )

    return {
        "query": term,
        "cases": [{"case_number": r[0], "title": r[1], "status": r[2]} for r in cases],
        "criminals": [{"secret_id": r[0], "name": r[1], "profile_type": r[2], "risk_level": r[3]} for r in criminals],
        "entities": [{"entity_id": r[0], "entity_type": r[1], "name": r[2], "case_id": r[3]} for r in entities],
        "sources": [{"source_id": r[0], "filename": r[1], "source_type": r[2], "case_id": r[3], "status": r[4]} for r in sources],
    }