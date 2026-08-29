"""Integration tests for database / graph connectivity.

Marked `integration` and skipped automatically when the external service is not
reachable, so the suite passes in environments without Docker/DBs running.

Run with real services:
    pytest -m integration
"""
import pytest

from app.core.dbcheck import check_database_connection
from app.core.graphcheck import check_graph_connection

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_postgres_reachable() -> None:
    result = await check_database_connection()
    assert result["status"] == "ok", f"PostgreSQL unreachable: {result}"


@pytest.mark.asyncio
async def test_neo4j_reachable() -> None:
    result = await check_graph_connection()
    assert result["status"] == "ok", f"Neo4j unreachable: {result}"
