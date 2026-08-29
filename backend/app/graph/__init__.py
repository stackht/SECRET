"""Graph layer.

Provides the knowledge-graph data-access abstraction and implementations:
- `GraphStore` protocol (domain operations)
- `Neo4jStore` (production, backed by Neo4j)
- `MemoryGraphStore` (in-memory implementation for tests / prototyping)
"""
from app.graph.types import GraphEdge, GraphNode, GraphSubgraph

__all__ = ["GraphEdge", "GraphNode", "GraphSubgraph"]
