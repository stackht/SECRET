"""Graph store protocol (Phase 6).

Defines the operations the graph layer must support. Implementations:
- `Neo4jStore` (production)
- `MemoryGraphStore` (tests / prototyping)

Keeping this as a Protocol allows the GraphService to be tested without a live
Neo4j instance and makes swapping storage engines trivial.
"""
from typing import Protocol, runtime_checkable

from app.graph.types import GraphEdge, GraphNode, GraphSubgraph


@runtime_checkable
class GraphStore(Protocol):
    """Knowledge-graph storage interface."""

    async def get_entity(self, entity_id: str) -> GraphNode | None:
        """Return a single node by id, or None."""
        ...

    async def get_relationships(self, entity_id: str) -> list[GraphEdge]:
        """Return edges touching the given node (both directions)."""
        ...

    async def get_neighbors(
        self,
        entity_id: str,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
    ) -> list[GraphNode]:
        """Return direct neighbors of a node, optionally filtered."""
        ...

    async def expand_neighborhood(
        self,
        entity_id: str,
        depth: int = 1,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
    ) -> GraphSubgraph:
        """Return the k-hop neighborhood (nodes + edges) of a node."""
        ...

    async def build_network(
        self,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
        limit: int = 500,
    ) -> GraphSubgraph:
        """Return a (filtered, bounded) slice of the whole graph."""
        ...

    async def upsert_node(self, node: GraphNode) -> None:
        """Create or update a node."""
        ...

    async def upsert_edge(self, edge: GraphEdge) -> None:
        """Create or update a relationship edge."""
        ...
