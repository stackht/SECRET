"""Criminal / entity endpoints (Phase 4)."""
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, RequireAnalyst
from app.schemas.criminal import (
    CriminalProfileCreate,
    CriminalProfileList,
    CriminalProfileRead,
    CriminalProfileUpdate,
)
from app.services.criminal_service import CriminalService

router = APIRouter()


@router.get(
    "",
    response_model=CriminalProfileList,
    summary="List / search criminal profiles",
)
async def list_profiles(
    session: DbSession,
    _user: CurrentUser,
    q: Annotated[str | None, Query(description="Free-text search")] = None,
    profile_type: Annotated[str | None, Query(description="Entity type filter")] = None,
    risk_level: Annotated[str | None, Query(description="Risk level filter")] = None,
    status: Annotated[str | None, Query(description="Profile status filter")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> CriminalProfileList:
    return await CriminalService(session).list_profiles(
        q=q, profile_type=profile_type, risk_level=risk_level,
        status=status, skip=skip, limit=limit,
    )


@router.get(
    "/{secret_id_or_id}",
    response_model=CriminalProfileRead,
    summary="Get a profile by secret_id (P-0421) or numeric id",
)
async def get_profile(
    secret_id_or_id: str,
    session: DbSession,
    _user: CurrentUser,
) -> object:
    return await CriminalService(session).get_profile(secret_id_or_id)


@router.post(
    "",
    response_model=CriminalProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a criminal profile",
)
async def create_profile(
    payload: CriminalProfileCreate,
    session: DbSession,
    _: RequireAnalyst,
) -> object:
    profile = await CriminalService(session).create_profile(payload)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.patch(
    "/{secret_id_or_id}",
    response_model=CriminalProfileRead,
    summary="Update a criminal profile",
)
async def update_profile(
    secret_id_or_id: str,
    payload: CriminalProfileUpdate,
    session: DbSession,
    _: RequireAnalyst,
) -> object:
    profile = await CriminalService(session).update_profile(secret_id_or_id, payload)
    await session.commit()
    await session.refresh(profile)
    return profile
