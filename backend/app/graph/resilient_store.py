"""Resilient graph store (Phase 2).

Wraps the Neo4j store so the application keeps working when Neo4j is
unreachable (offline demo, dev machines without Docker): the first failing
operation transparently switches to the in-memory store. Honest degradation —
no fake data, the graph endpoints simply serve whatever the in-memory store has
been materialized into during this process run.
"""
from typing import Any

from app.graph.memory_store import MemoryGraphStore
from app.graph.neo4j_store import Neo4jStore

_METHODS = (
    "get_entity",
    "get_relationships",
    "get_neighbors",
    "expand_neighborhood",
    "build_network",
    "upsert_node",
    "upsert_edge",
)


class ResilientGraphStore:
    """Neo4j-backed store that falls back to memory on first connection failure."""

    def __init__(self, primary: Any = None) -> None:
        self._primary = primary if primary is not None else Neo4jStore()
        self._fallback: MemoryGraphStore | None = None

    async def _exec(self, name: str, *args: Any, **kwargs: Any) -> Any:
        store = self._fallback if self._fallback is not None else self._primary
        try:
            return await getattr(store, name)(*args, **kwargs)
        except Exception:
            if store is not self._fallback:
                self._fallback = MemoryGraphStore()
                return await getattr(self._fallback, name)(*args, **kwargs)
            raise

    def __getattr__(self, name: str) -> Any:
        if name in _METHODS:
            async def _method(*args: Any, **kwargs: Any) -> Any:
                return await self._exec(name, *args, **kwargs)

            return _method
        raise AttributeError(name)