"""Audit endpoints (original Phase 13)."""
from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.audit import AuditEntryRead, AuditRequest
from app.services.audit_service import AuditService

router = APIRouter()


@router.get(
    "",
    response_model=list[AuditEntryRead],
    summary="List recent audit entries",
)
async def list_audit(
    session: DbSession,
    user: CurrentUser,
    limit: int = 50,
) -> list[AuditEntryRead]:
    entries = await AuditService(session).list_recent(limit=limit)
    return [
        AuditEntryRead(
            id=e.id,
            user_id=e.user_id,
            action=e.action,
            object_type=e.object_type,
            object_id=e.object_id,
            result=e.result or {},
            created_at=e.created_at,
        )
        for e in entries
    ]


@router.post(
    "",
    response_model=AuditEntryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record an audit action",
)
async def record_audit(
    payload: AuditRequest,
    session: DbSession,
    user: CurrentUser,
) -> AuditEntryRead:
    entry = await AuditService(session).record(
        user=user,
        action=payload.action,
        object_type=payload.object_type,
        object_id=payload.object_id,
        result=payload.result,
    )
    await session.commit()
    return AuditEntryRead(
        id=entry.id,
        user_id=entry.user_id,
        action=entry.action,
        object_type=entry.object_type,
        object_id=entry.object_id,
        result=entry.result or {},
        created_at=entry.created_at,
    )
