"""Case alert endpoints (Phase 18)."""
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession, RequireAnalyst
from app.schemas.alert import AlertGenerateResult, AlertRead, AlertStatusUpdate
from app.services.alert_service import AlertService

router = APIRouter()


def _to_read(a) -> AlertRead:
    return AlertRead(
        id=a.id,
        case_id=a.case_id,
        profile_id=a.profile_id,
        severity=a.severity,
        status=a.status,
        title=a.title,
        description=a.description,
        score=a.score,
        confidence=a.confidence,
        source_ids=a.source_ids,
        reviewed_by=a.reviewed_by,
        reviewed_at=a.reviewed_at,
        created_at=a.created_at,
    )


@router.get("/{case_key}/alerts", response_model=list[AlertRead], summary="Case alerts")
async def list_alerts(case_key: str, session: DbSession, user: CurrentUser) -> list[AlertRead]:
    alerts = await AlertService(session).list(case_key, user)
    return [_to_read(a) for a in alerts]


@router.post(
    "/{case_key}/alerts/generate",
    response_model=AlertGenerateResult,
    summary="Generate indicator alerts from persisted analytics",
)
async def generate_alerts(case_key: str, session: DbSession, _: RequireAnalyst) -> AlertGenerateResult:
    from app.repositories.case_repository import CaseRepository

    case_analyzer = AlertService(session)
    cases = CaseRepository(session)
    case = await cases.get_by_case_number(case_key)
    if case is None and case_key.isdigit():
        case = await cases.get(int(case_key))
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    created = await case_analyzer.generate(case.id)
    await session.commit()
    return AlertGenerateResult(created=len(created), alerts=[_to_read(a) for a in created])


@router.patch(
    "/{case_key}/alerts/{alert_id}",
    response_model=AlertRead,
    summary="Review / dismiss / resolve an alert",
)
async def update_alert(
    case_key: str, alert_id: int, payload: AlertStatusUpdate, session: DbSession, user: CurrentUser
) -> AlertRead:
    alert = await AlertService(session).transition(case_key, alert_id, user, payload.status)
    await session.commit()
    await session.refresh(alert)
    return _to_read(alert)