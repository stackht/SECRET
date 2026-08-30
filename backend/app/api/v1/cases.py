"""Case / investigation endpoints (Phase 5)."""
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, RequireAnalyst
from app.schemas.case import (
    CaseAssociateRequest,
    CaseCreate,
    CaseDetail,
    CaseList,
    CaseRead,
    CaseUpdate,
)
from app.schemas.criminal import CriminalProfileRead
from app.services.case_service import CaseService

router = APIRouter()


@router.get(
    "",
    response_model=CaseList,
    summary="List / search cases",
)
async def list_cases(
    session: DbSession,
    _user: CurrentUser,
    q: Annotated[str | None, Query(description="Free-text search on title / case number")] = None,
    status: Annotated[str | None, Query(description="Case status filter")] = None,
    priority: Annotated[str | None, Query(description="Case priority filter")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> CaseList:
    return await CaseService(session).list_cases(q=q, status_=status, priority=priority, skip=skip, limit=limit)


@router.post(
    "",
    response_model=CaseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a case",
)
async def create_case(
    payload: CaseCreate,
    session: DbSession,
    _: RequireAnalyst,
) -> object:
    case = await CaseService(session).create_case(payload)
    await session.commit()
    await session.refresh(case)
    return case


@router.get(
    "/{case_number_or_id}",
    response_model=CaseDetail,
    summary="Get a case (with associated profiles)",
)
async def get_case(
    case_number_or_id: str,
    session: DbSession,
    _user: CurrentUser,
) -> CaseDetail:
    return await CaseService(session).get_case_detail(case_number_or_id)


@router.patch(
    "/{case_number_or_id}",
    response_model=CaseRead,
    summary="Update a case",
)
async def update_case(
    case_number_or_id: str,
    payload: CaseUpdate,
    session: DbSession,
    _: RequireAnalyst,
) -> object:
    case = await CaseService(session).update_case(case_number_or_id, payload)
    await session.commit()
    await session.refresh(case)
    return case


@router.get(
    "/{case_number_or_id}/profiles",
    response_model=list[CriminalProfileRead],
    summary="List criminal profiles associated with a case",
)
async def list_case_profiles(
    case_number_or_id: str,
    session: DbSession,
    _user: CurrentUser,
) -> list[CriminalProfileRead]:
    return await CaseService(session).list_case_profiles(case_number_or_id)


@router.post(
    "/{case_number_or_id}/profiles",
    response_model=CaseDetail,
    status_code=status.HTTP_200_OK,
    summary="Associate a criminal profile with a case",
)
async def associate_profile(
    case_number_or_id: str,
    payload: CaseAssociateRequest,
    session: DbSession,
    _: RequireAnalyst,
) -> CaseDetail:
    await CaseService(session).associate_profile(
        case_number_or_id, payload.profile_id, payload.role_in_case
    )
    await session.commit()
    return await CaseService(session).get_case_detail(case_number_or_id)


@router.delete(
    "/{case_number_or_id}/profiles/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dissociate a criminal profile from a case",
)
async def dissociate_profile(
    case_number_or_id: str,
    profile_id: int,
    session: DbSession,
    _: RequireAnalyst,
) -> None:
    await CaseService(session).dissociate_profile(case_number_or_id, profile_id)
    await session.commit()


@router.delete(
    "/{case_number_or_id}",
    response_model=CaseRead,
    summary="Archive (soft-remove) a case",
)
async def archive_case(
    case_number_or_id: str,
    session: DbSession,
    _: RequireAnalyst,
) -> object:
    case = await CaseService(session).archive_case(case_number_or_id)
    await session.commit()
    await session.refresh(case)
    return case
