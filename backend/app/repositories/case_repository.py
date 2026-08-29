"""Case data-access repository (Phase 5)."""
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseCriminal
from app.models.criminal import CriminalProfile
from app.repositories.base import BaseRepository


@dataclass
class CaseFilters:
    """Optional filters when listing cases."""

    q: str | None = None
    status: str | None = None
    priority: str | None = None


class CaseRepository(BaseRepository[Case]):
    """Async repository for Case records and profile associations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Case)

    async def get_by_case_number(self, case_number: str) -> Case | None:
        return await self.get_by(case_number=case_number)

    def _apply_filters(self, stmt, filters: CaseFilters):
        if filters.q:
            like = f"%{filters.q}%"
            stmt = stmt.where(or_(Case.title.ilike(like), Case.case_number.ilike(like)))
        if filters.status:
            stmt = stmt.where(Case.status == filters.status)
        if filters.priority:
            stmt = stmt.where(Case.priority == filters.priority)
        return stmt

    async def list_cases(
        self, filters: CaseFilters, skip: int = 0, limit: int = 50
    ) -> list[Case]:
        stmt = self._apply_filters(select(Case).order_by(Case.id.desc()), filters)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_cases(self, filters: CaseFilters) -> int:
        stmt = self._apply_filters(select(func.count(Case.id)), filters)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    # --- profile associations (case_criminals) ---

    async def associate_profile(
        self, case_id: int, profile_id: int, role_in_case: str | None = None
    ) -> CaseCriminal | None:
        existing = await self._session.get(CaseCriminal, (case_id, profile_id))
        if existing is not None:
            return None
        link = CaseCriminal(case_id=case_id, profile_id=profile_id, role_in_case=role_in_case)
        self._session.add(link)
        await self._session.flush()
        return link

    async def dissociate_profile(self, case_id: int, profile_id: int) -> bool:
        link = await self._session.get(CaseCriminal, (case_id, profile_id))
        if link is None:
            return False
        await self._session.delete(link)
        await self._session.flush()
        return True

    async def list_case_profiles(self, case_id: int) -> list[CriminalProfile]:
        stmt = (
            select(CriminalProfile)
            .join(CaseCriminal, CaseCriminal.profile_id == CriminalProfile.id)
            .where(CaseCriminal.case_id == case_id)
            .order_by(CriminalProfile.id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_case_profiles(self, case_id: int) -> int:
        stmt = select(func.count()).select_from(CaseCriminal).where(CaseCriminal.case_id == case_id)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
