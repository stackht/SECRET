"""Global search endpoint (Phase 21)."""
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.services.search_service import global_search

router = APIRouter()


@router.get("", summary="Global search across cases, entities and sources")
async def search(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    session: DbSession,
    _user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> dict:
    return await global_search(session, q, limit)