"""Graph store selection (Phase 6).

Provides the default `GraphStore` instance. In production this is the Neo4j
store; tests override the dependency with an in-memory store.
"""
from app.graph.neo4j_store import Neo4jStore

_graph_store = None


def get_graph_store():
    """Return the default production graph store (Neo4j-backed singleton)."""
    global _graph_store
    if _graph_store is None:
        _graph_store = Neo4jStore()
    return _graph_store
