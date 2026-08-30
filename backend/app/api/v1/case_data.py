"""Persisted entity + relationship endpoints (Phase 2 read path).

Read-back the canonical entities / relationships extracted from ingested
sources for a case, with provenance (source_ids) and confidence.
"""
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.models.case import Case
from app.repositories.case_repository import CaseRepository
from app.repositories.entity_repository import EntityRepository, RelationshipRepository
from app.schemas.case_analytics import CommsResponse, LocationsResponse, TimelineEvent, TransResponse
from app.schemas.entity import EntityRead, RelationshipRead
from app.services.case_analytics import CaseAnalyticsService

router = APIRouter()


async def _resolve_case(session, case_key: str) -> Case:
    repo = CaseRepository(session)
    case = await repo.get_by_case_number(case_key)
    if case is not None:
        return case
    if case_key.isdigit():
        case = await repo.get(int(case_key))
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get(
    "/{case_key}/entities",
    response_model=list[EntityRead],
    summary="Persisted entities extracted for a case",
)
async def list_case_entities(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> list[EntityRead]:
    case = await _resolve_case(session, case_key)
    rows = await EntityRepository(session).list_by_case(case.id)
    return [
        EntityRead(
            entity_id=e.entity_id,
            entity_type=e.entity_type,
            name=e.name,
            confidence=e.confidence,
            attributes=e.attributes,
            source_ids=e.source_ids,
            created_at=e.created_at,
        )
        for e in rows
    ]


@router.get(
    "/{case_key}/relationships",
    response_model=list[RelationshipRead],
    summary="Persisted relationships extracted for a case",
)
async def list_case_relationships(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> list[RelationshipRead]:
    case = await _resolve_case(session, case_key)
    rows = await RelationshipRepository(session).list_by_case(case.id)
    return [
        RelationshipRead(
            rel_type=r.rel_type,
            source_id=r.source_id,
            target_id=r.target_id,
            confidence=r.confidence,
            source_ids=r.source_ids,
            attributes=r.attributes,
            created_at=r.created_at,
        )
        for r in rows
    ]


# --- Per-case analysis (comms / transactions / timeline / locations) -----------

@router.get(
    "/{case_key}/communications",
    response_model=CommsResponse,
    summary="Communication analysis from persisted CDR relationships",
)
async def case_communications(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> CommsResponse:
    case = await _resolve_case(session, case_key)
    return CommsResponse(**await CaseAnalyticsService(session).communications(case.id))


@router.get(
    "/{case_key}/transactions",
    response_model=TransResponse,
    summary="Transaction analysis from persisted transfer edges",
)
async def case_transactions(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> TransResponse:
    case = await _resolve_case(session, case_key)
    return TransResponse(**await CaseAnalyticsService(session).transactions(case.id))


@router.get(
    "/{case_key}/timeline",
    response_model=list[TimelineEvent],
    summary="Unified case timeline from all ingested sources",
)
async def case_timeline(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> list[TimelineEvent]:
    case = await _resolve_case(session, case_key)
    return [TimelineEvent(**e) for e in await CaseAnalyticsService(session).timeline(case.id)]


@router.get(
    "/{case_key}/locations",
    response_model=LocationsResponse,
    summary="Location intelligence from ingested location entities",
)
async def case_locations(
    case_key: str,
    session: DbSession,
    _user: CurrentUser,
) -> LocationsResponse:
    case = await _resolve_case(session, case_key)
    return LocationsResponse(**await CaseAnalyticsService(session).locations(case.id))