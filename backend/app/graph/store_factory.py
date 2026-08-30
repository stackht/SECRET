"""Graph store selection (Phase 6).

Provides the default `GraphStore` instance. In production this is a
Neo4j-backed store with graceful in-memory fallback; tests override the
dependency with an in-memory store.
"""
from app.graph.resilient_store import ResilientGraphStore

_graph_store = None


def get_graph_store():
    """Return the default graph store (Neo4j-backed, resilient singleton)."""
    global _graph_store
    if _graph_store is None:
        _graph_store = ResilientGraphStore()
    return _graph_store
