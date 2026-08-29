"""AI assistant tests (original Phase 11)."""
import pytest

from app.graph.memory_store import MemoryGraphStore
from app.graph.types import GraphEdge, GraphNode
from app.services.assistant_service import LocalDatasetAssistant


def _store_with_entity() -> MemoryGraphStore:
    store = MemoryGraphStore()
    store.nodes["P-0421"] = GraphNode(id="P-0421", type="PERSON", name="Person A")
    store.nodes["O-1101"] = GraphNode(id="O-1101", type="ORGANIZATION", name="Org Orion")
    store.edges["E1"] = GraphEdge(id="E1", source_id="P-0421", target_id="O-1101", type="MEMBER_OF")
    return store


@pytest.mark.asyncio
async def test_connections_returns_neighbors_with_source():
    assistant = LocalDatasetAssistant(_store_with_entity())
    result = await assistant.answer("Show connections of P-0421")
    assert result.found is True
    assert "O-1101" in result.answer
    assert result.source_ids  # supporting source provided


@pytest.mark.asyncio
async def test_unknown_entity_no_evidence():
    assistant = LocalDatasetAssistant(_store_with_entity())
    result = await assistant.answer("Show connections of P-9999")
    assert result.found is False
    assert "No supporting evidence" in result.answer
    assert result.source_ids == []


@pytest.mark.asyncio
async def test_no_entity_id_asks_for_clarification():
    assistant = LocalDatasetAssistant(_store_with_entity())
    result = await assistant.answer("What anomalies were detected?")
    assert result.found is False
