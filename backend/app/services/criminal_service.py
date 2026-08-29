"""Criminal profile service (Phase 4)."""
from fastapi import HTTPException, status

from app.models.criminal import CriminalProfile
from app.repositories.criminal_repository import CriminalRepository, ProfileFilters
from app.schemas.criminal import (
    CriminalProfileCreate,
    CriminalProfileList,
    CriminalProfileUpdate,
)
from app.utils.ids import build_secret_id


class CriminalService:
    """Business logic for criminal/entity profiles."""

    def __init__(self, session) -> None:
        self._repo = CriminalRepository(session)

    async def list_profiles(
        self,
        q: str | None,
        profile_type: str | None,
        risk_level: str | None,
        status: str | None,
        skip: int,
        limit: int,
    ) -> CriminalProfileList:
        filters = ProfileFilters(q=q, profile_type=profile_type, risk_level=risk_level, status=status)
        total = await self._repo.count_profiles(filters)
        items = await self._repo.list_profiles(filters, skip=skip, limit=limit)
        return CriminalProfileList(total=total, limit=limit, offset=skip, items=items)

    async def get_profile(self, secret_id_or_id: str) -> CriminalProfile:
        profile = await self._resolve_secret_id(secret_id_or_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return profile

    async def _resolve_secret_id(self, key: str) -> CriminalProfile | None:
        """Resolve a 'P-0421' style secret_id OR a plain numeric id."""
        profile = await self._repo.get_by_secret_id(key)
        if profile is not None:
            return profile
        if key.isdigit():
            return await self._repo.get(int(key))
        return None

    async def create_profile(self, payload: CriminalProfileCreate) -> CriminalProfile:
        data = payload.model_dump()
        profile_type = data.pop("profile_type").value  # enum -> string
        data["profile_type"] = profile_type
        profile = await self._repo.create(**data)
        # secret_id is derived from the assigned DB id for a stable identifier.
        profile.secret_id = build_secret_id(profile_type, profile.id)
        return await self._repo.save(profile)

    async def update_profile(self, secret_id_or_id: str, payload: CriminalProfileUpdate) -> CriminalProfile:
        profile = await self._resolve_secret_id(secret_id_or_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        data = payload.model_dump(exclude_unset=True)
        if "risk_level" in data and data["risk_level"] is not None:
            data["risk_level"] = data["risk_level"].value
        for key, value in data.items():
            setattr(profile, key, value)
        return await self._repo.save(profile)
