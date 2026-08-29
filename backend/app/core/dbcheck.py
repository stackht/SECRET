"""PostgreSQL connectivity helpers (Phase 2).

These are used by the health endpoint and by the connection-verification tests.
They intentionally perform lightweight checks and do not depend on models.
"""
from sqlalchemy import text

from app.core.database import engine


async def check_database_connection() -> dict[str, str]:
    """Run a trivial query against the configured database.

    Returns {"status": "ok"} on success, or {"status": "error", "detail": ...}.
    No exception is raised; callers decide how to surface failures.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - depends on DB availability
        return {"status": "error", "detail": str(exc)}
