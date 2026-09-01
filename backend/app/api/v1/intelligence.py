"""Case intelligence endpoints (Phase 15).

Expose the unified intelligence layer: full case intelligence, hidden links,
network DNA, leads, and what-if simulation. Results are analytical — decision
support, never a guilt finding.
"""
from __future__ import annotations

import networkx as nx
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.repositories.case_repository import CaseRepository
from app.services.case_intelligence_service import CaseIntelligenceService
from app.intelligence import simulate

router = APIRouter()

# Per-process cache of computed intelligence per case id.
_cache: dict[int, dict] = {}


def _d(dataclass_obj) -> dict:
    from dataclasses import asdict
    return asdict(dataclass_obj)


async def _resolve_case_id(session, case_key: str) -> int:
    repo = CaseRepository(session)
    case = await repo.get_by_case_number(case_key)
    if case is not None:
        return case.id
    if case_key.isdigit():
        c = await repo.get(int(case_key))
        if c is not None:
            return c.id
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")


@router.get("/{case_key}/intelligence", summary="Full unified case intelligence")
async def get_intelligence(case_key: str, session: DbSession, _user: CurrentUser) -> dict:
    case_id = await _resolve_case_id(session, case_key)
    return await CaseIntelligenceService(session).build(case_id, cache=_cache)


@router.get("/{case_key}/hidden-links", summary="Potential / hidden link discovery")
async def hidden_links(case_key: str, session: DbSession, _user: CurrentUser) -> list[dict]:
    case_id = await _resolve_case_id(session, case_key)
    result = await CaseIntelligenceService(session).build(case_id, cache=_cache)
    return result["potential_links"]  # already serialized by the unified service


@router.get("/{case_key}/network-dna", summary="Network analytical fingerprint")
async def network_dna(case_key: str, session: DbSession, _user: CurrentUser) -> dict:
    case_id = await _resolve_case_id(session, case_key)
    result = await CaseIntelligenceService(session).build(case_id, cache=_cache)
    return result["network_dna"]


@router.post("/{case_key}/simulate", summary="What-if investigation simulation")
async def what_if(
    case_key: str,
    payload: dict,
    session: DbSession,
    _user: CurrentUser,
) -> dict:
    case_id = await _resolve_case_id(session, case_key)
    op = payload.get("operation")
    subject = payload.get("subject")
    if op not in ("remove_entity", "remove_relationship", "add_relationship", "confirm_potential", "hide_entity"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid operation")
    if not subject:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="subject required")

    # Build the current graph from persisted entities/relationships.
    data = await _load_case_data(session, case_id)
    graph = nx.Graph()
    for e in data.entities:
        graph.add_node(e.id, type=e.type, name=e.name)
    for r in data.relationships:
        graph.add_edge(r.source, r.target, type=r.rel_type, weight=r.strength or r.confidence)

    result = simulate.simulate(graph, op, subject)
    return _d(result)


async def _load_case_data(session, case_id):
    from app.repositories.case_analytics_repo import build_case_data
    return await build_case_data(session, case_id)