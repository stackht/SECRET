"""Generic async repository base.

Provides common CRUD primitives over SQLAlchemy async sessions. Concrete
repositories inherit from this to avoid duplicating query code.
"""
from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Async repository operating on a single model type."""

    def __init__(self, session: AsyncSession, model: Type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def create(self, **values: object) -> ModelT:
        instance = self._model(**values)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def save(self, instance: ModelT) -> ModelT:
        """Stage an instance for update and flush (idempotent; caller commits)."""
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Stage an instance for deletion and flush (caller commits)."""
        await self._session.delete(instance)
        await self._session.flush()

    async def get(self, pk: int) -> Optional[ModelT]:
        return await self._session.get(self._model, pk)

    async def get_by(self, **filters: object) -> Optional[ModelT]:
        stmt = select(self._model).filter_by(**filters).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
