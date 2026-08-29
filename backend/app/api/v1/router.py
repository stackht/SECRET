"""V1 API route aggregator.

Mounts all version-1 routers under the /api/v1 prefix.
Phase 2: health wired; auth/criminals/cases/graph routers are registered and
gain endpoints in Phases 3-6.
"""
from fastapi import APIRouter

from app.api.v1 import analysis, audit, auth, cases, criminals, graph, health, reports

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(criminals.router, prefix="/criminals", tags=["criminals"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
