"""Database engine / session factory (async SQLAlchemy 2.0).

Phase 1: scaffolding. The async engine + session factory are configured here
so Phase 2 simply imports them. No models are registered yet.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    echo=False,
    future=True,
    # Never block startup/hang when the DB is unreachable: bound the connect
    # attempt (asyncpg uses `timeout` seconds) and reap idle pools quickly.
    connect_args={"timeout": 5} if _settings.database_url.startswith("postgresql") else {},
    pool_pre_ping=True,
    pool_recycle=1800,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models (Phase 2)."""


async def get_db_session() -> AsyncSession:
    """FastAPI dependency: yield an async session."""
    async with async_session_factory() as session:
        yield session
