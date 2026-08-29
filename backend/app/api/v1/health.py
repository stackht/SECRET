"""Health endpoints (Phase 2).

Provides service + database + graph connectivity status for operations and CI.
"""
from fastapi import APIRouter, status

from app.core.dbcheck import check_database_connection
from app.core.graphcheck import check_graph_connection

router = APIRouter(tags=["health"])


@router.get(
    "/health/db",
    summary="Database connectivity",
    responses={
        200: {"description": "Database reachable"},
        503: {"description": "Database unreachable"},
    },
)
async def health_db() -> dict[str, str]:
    """Return 200 if PostgreSQL is reachable, else 503."""
    result = await check_database_connection()
    if result["status"] != "ok":
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result)
    return result


@router.get(
    "/health/graph",
    summary="Graph connectivity",
    responses={
        200: {"description": "Neo4j reachable"},
        503: {"description": "Neo4j unreachable"},
    },
)
async def health_graph() -> dict[str, str]:
    """Return 200 if Neo4j is reachable, else 503."""
    result = await check_graph_connection()
    if result["status"] != "ok":
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result)
    return result
