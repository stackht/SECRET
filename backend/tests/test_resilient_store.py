"""Resilient graph store fallback tests (Phase 2)."""
import asyncio

from app.graph.resilient_store import ResilientGraphStore
from app.graph.types import GraphNode


class _BrokenStore:
    async def get_entity(self, entity_id: str) -> GraphNode:
        raise RuntimeError("Neo4j unreachable")

    async def build_network(self, **kwargs):
        raise RuntimeError("Neo4j unreachable")

    async def upsert_node(self, node: GraphNode) -> None:
        raise RuntimeError("Neo4j unreachable")


class _HealthCheckStore:
    async def get_entity(self, entity_id: str) -> GraphNode:
        return GraphNode(id=entity_id, type="PERSON", name="Healthy")


def test_falls_back_to_memory_on_failure() -> None:
    store = ResilientGraphStore(primary=_BrokenStore())

    async def scenario() -> GraphNode:
        await store.upsert_node(GraphNode(id="P-1", type="PERSON", name="Local"))
        node = await store.get_entity("P-1")
        assert node is not None and node.name == "Local"
        return node

    assert asyncio.run(scenario()).id == "P-1"
    assert store._fallback is not None  # type: ignore[attr-defined]


def test_primary_used_when_healthy() -> None:
    store = ResilientGraphStore(primary=_HealthCheckStore())
    node = asyncio.run(store.get_entity("P-2"))
    assert node is not None and node.name == "Healthy"
    assert store._fallback is None  # type: ignore[attr-defined]