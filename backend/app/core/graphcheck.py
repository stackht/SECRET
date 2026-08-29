"""Neo4j connectivity helpers (Phase 2).

Lightweight driver health check used by the health endpoint and tests.
"""
from app.core.neo4j import neo4j_connection


async def check_graph_connection() -> dict[str, str]:
    """Ping the Neo4j server.

    Returns {"status": "ok"} on success, or {"status": "error", "detail": ...}.
    """
    try:
        driver = neo4j_connection.driver
        async with driver.session() as session:
            await session.run("RETURN 1")
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - depends on DB availability
        return {"status": "error", "detail": str(exc)}
