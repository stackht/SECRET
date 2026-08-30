"""pytest configuration for SECRET backend."""
import os

# Test mode: the app-level lifespan skips seeding + engine disposal (avoiding
# Windows proactor teardown races). Integration markers are always skipped in
# test mode — unit runs must never depend on live PostgreSQL/Neo4j.
os.environ.setdefault("SECRET_ENV", "test")

import pytest
from fastapi.testclient import TestClient

# Ensure app is importable regardless of CWD.
os.environ.setdefault("PYTHONPATH", ".")

from app.core.dbcheck import check_database_connection  # noqa: E402
from app.core.graphcheck import check_graph_connection  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a TestClient bound to the FastAPI app (lifespan runs).

    Used for non-DB tests (health, bootstrap). The lifespan attempts a best-effort
    seed against the configured engine but fails silently if the DB is down.
    """
    from app.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_client() -> TestClient:
    """Return a TestClient whose DB sessions point at a fresh SQLite database.

    Creates tables (via ORM metadata) and seeds the default admin user, enabling
    auth and repository tests to run without PostgreSQL/Neo4j/Docker.
    """
    import asyncio

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.api.deps import get_graph_store
    from app.core.database import Base, get_db_session
    from app.graph.memory_store import MemoryGraphStore
    from app.main import create_app
    from app.services.seed_service import ensure_admin_user

    async def _setup():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        TestSession = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with TestSession() as session:
            await ensure_admin_user(session)
        return engine, TestSession

    engine, test_session = asyncio.run(_setup())

    async def override_session():
        async with test_session() as session:
            yield session

    from app.main import app as _app

    memory_store = MemoryGraphStore()
    _app.dependency_overrides[get_db_session] = override_session
    _app.dependency_overrides[get_graph_store] = lambda: memory_store
    with TestClient(_app) as test_client:
        yield test_client
    _app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: requires external services (PostgreSQL / Neo4j) to be running",
    )


def pytest_collection_modifyitems(session, config, items) -> None:  # type: ignore[no-untyped-def]
    """Force-skip integration tests in test mode.

    Unit runs are deterministic and must never depend on live PostgreSQL/Neo4j.
    (Outside test mode we additionally auto-skip them when services are down.)
    """
    if os.environ.get("SECRET_ENV") == "test":
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="integration disabled under SECRET_ENV=test"))
        return

    import asyncio

    async def _probe() -> tuple[bool, bool]:
        db_ok = (await check_database_connection()).get("status") == "ok"
        graph_ok = (await check_graph_connection()).get("status") == "ok"
        return db_ok, graph_ok

    try:
        db_ok, graph_ok = asyncio.run(_probe())
    except Exception:  # noqa: BLE001 - never let probe failure break collection
        db_ok = graph_ok = False

    for item in items:
        if "integration" in item.keywords:
            if not (db_ok and graph_ok):
                item.add_marker(
                    pytest.mark.skip(
                        reason="external services unreachable (PostgreSQL/Neo4j not running)"
                    )
                )
