"""Case service (Phase 5)."""
from datetime import datetime

from fastapi import HTTPException, status

from app.models.case import Case
from app.repositories.case_repository import CaseFilters, CaseRepository
from app.repositories.criminal_repository import CriminalRepository
from app.schemas.case import CaseCreate, CaseDetail, CaseList, CaseRead, CaseUpdate
from app.schemas.criminal import CriminalProfileRead


class CaseService:
    """Business logic for investigations (cases)."""

    def __init__(self, session) -> None:
        self._repo = CaseRepository(session)
        self._profiles = CriminalRepository(session)

    async def list_cases(
        self, q: str | None, status_: str | None, priority: str | None,
        skip: int, limit: int,
    ) -> CaseList:
        filters = CaseFilters(q=q, status=status_, priority=priority)
        total = await self._repo.count_cases(filters)
        items = await self._repo.list_cases(filters, skip=skip, limit=limit)
        return CaseList(total=total, limit=limit, offset=skip, items=items)

    async def get_case_detail(self, case_number_or_id: str) -> CaseDetail:
        case = await self._resolve(case_number_or_id)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        base = CaseRead.model_validate(case)
        profiles = await self._repo.list_case_profiles(case.id)
        return CaseDetail(
            **base.model_dump(),
            profiles=[CriminalProfileRead.model_validate(p) for p in profiles],
        )

    async def _resolve(self, key: str) -> Case | None:
        case = await self._repo.get_by_case_number(key)
        if case is not None:
            return case
        if key.isdigit():
            return await self._repo.get(int(key))
        return None

    async def create_case(self, payload: CaseCreate) -> Case:
        data = payload.model_dump(exclude_unset=True)
        for field in ("status", "priority"):
            if data.get(field) is not None:
                data[field] = data[field].value
        case = await self._repo.create(**data)
        if not case.case_number:
            # Deterministic, unique-looking case number derived from DB id.
            case.case_number = f"CASE-{datetime.now().year}-{case.id:04d}"
            await self._repo.save(case)
        return case

    async def update_case(self, case_number_or_id: str, payload: CaseUpdate) -> Case:
        case = await self._resolve(case_number_or_id)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        data = payload.model_dump(exclude_unset=True)
        for field in ("status", "priority"):
            if data.get(field) is not None:
                data[field] = data[field].value
        for key, value in data.items():
            setattr(case, key, value)
        return await self._repo.save(case)

    # --- associations ---

    async def _get_case_checked(self, key: str) -> Case:
        case = await self._resolve(key)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case

    async def _get_profile_checked(self, profile_id: int):
        profile = await self._profiles.get(profile_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return profile

    async def associate_profile(self, case_key: str, profile_id: int, role: str | None):
        case = await self._get_case_checked(case_key)
        await self._get_profile_checked(profile_id)
        link = await self._repo.associate_profile(case.id, profile_id, role)
        if link is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Profile already associated with case"
            )
        return case

    async def dissociate_profile(self, case_key: str, profile_id: int) -> None:
        case = await self._get_case_checked(case_key)
        removed = await self._repo.dissociate_profile(case.id, profile_id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not associated with case"
            )

    async def list_case_profiles(self, case_key: str) -> list[CriminalProfileRead]:
        case = await self._get_case_checked(case_key)
        profiles = await self._repo.list_case_profiles(case.id)
        return [CriminalProfileRead.model_validate(p) for p in profiles]
