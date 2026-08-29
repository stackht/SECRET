"""Temporal/location + investigation workflow endpoints (Phases 9-10)."""
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession, GraphStoreDep, RequireAnalyst
from app.ingestion.generator import generate_synthetic
from app.schemas.analysis import TemporalLocationResponse
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.analysis_service import TemporalLocationService
from app.services.assistant_service import LocalDatasetAssistant
from app.services.investigation_engine import InvestigationEngine
from app.services.simulation_service import SimulationService

router = APIRouter()


@router.get(
    "/temporal-location",
    response_model=TemporalLocationResponse,
    summary="Temporal + location correlation over source records",
)
async def temporal_location(
    _user: CurrentUser,
    scenario: Annotated[str, Query(description="Synthetic data scenario")] = "NORMAL_NETWORK",
    entity_id: Annotated[str | None, Query(description="Filter events to one entity")] = None,
) -> TemporalLocationResponse:
    service = TemporalLocationService()
    events = generate_synthetic(scenario)
    return service.analyze(events, scenario=scenario, entity_id=entity_id)


@router.post(
    "/investigation",
    summary="Run the full investigation workflow over a scenario",
)
async def run_investigation(
    store: GraphStoreDep,
    session: DbSession,
    _: RequireAnalyst,
    scenario: Annotated[str, Query()] = "NORMAL_NETWORK",
) -> dict:
    """Execute generate -> ingest -> extract -> resolve -> graph -> analyze."""
    summary = await InvestigationEngine(store).run(scenario=scenario)
    await session.commit()
    return summary


@router.post(
    "/assistant",
    response_model=AssistantResponse,
    summary="Ask the local dataset analyst a question (evidence-grounded)",
)
async def assistant(
    payload: AssistantRequest,
    store: GraphStoreDep,
    _user: CurrentUser,
) -> AssistantResponse:
    result = await LocalDatasetAssistant(store).answer(payload.question)
    return AssistantResponse(
        question=result.question,
        answer=result.answer,
        source_ids=result.source_ids,
        found=result.found,
    )


@router.post(
    "/simulation",
    summary="Run the full intelligence simulation pipeline",
)
async def run_simulation(
    store: GraphStoreDep,
    _user: CurrentUser,
    scenario: Annotated[str, Query()] = "NORMAL_NETWORK",
) -> dict:
    return await SimulationService(store).run(scenario=scenario)
