"""Dashboard summary endpoint (Command Center)."""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.services.dashboard_service import dashboard_summary

router = APIRouter()


@router.get("/summary", summary="Live dashboard counters")
async def get_summary(session: DbSession, _user: CurrentUser) -> dict:
    return await dashboard_summary(session)