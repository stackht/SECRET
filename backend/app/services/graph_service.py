"""Graph service (Phase 6).

Coordinates graph queries against a `GraphStore`, converting domain types into
API schemas. Uses a store injected by FastAPI dependency resolution (Neo4j in
production, in-memory in tests).
"""
from typing import Any

from fastapi import HTTPException, status

from app.graph.types import GraphEdge, GraphNode, GraphSubgraph
from app.schemas.graph import GraphEdgeSchema, GraphNodeSchema, GraphResponse


def _jsonable(value: Any) -> Any:
    """Convert graph property values into JSON-serializable primitives.

    Neo4j returns its own temporal types (DateTime/Date/Time/Duration) that
    Pydantic cannot serialize; temporal properties are emitted as ISO strings.
    Lists and nested maps are converted recursively.
    """
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    try:
        from neo4j import time as neo4j_time  # installed with the driver
    except ImportError:  # pragma: no cover
        neo4j_time = None
    if neo4j_time is not None:
        if isinstance(value, (neo4j_time.DateTime, neo4j_time.Date, neo4j_time.Time)):
            return value.isoformat()
        if isinstance(value, neo4j_time.Duration):
            return str(value)
    return value


def _node_to_schema(node: GraphNode) -> GraphNodeSchema:
    return GraphNodeSchema(
        id=node.id,
        type=node.type,
        name=node.name,
        properties={k: _jsonable(v) for k, v in (node.properties or {}).items()},
    )


def _edge_to_schema(edge: GraphEdge) -> GraphEdgeSchema:
    return GraphEdgeSchema(
        id=edge.id,
        source=edge.source_id,
        target=edge.target_id,
        type=edge.type,
        properties={k: _jsonable(v) for k, v in (edge.properties or {}).items()},
    )


def _subgraph_to_response(subgraph: GraphSubgraph) -> GraphResponse:
    return GraphResponse(
        nodes=[_node_to_schema(n) for n in subgraph.nodes],
        edges=[_edge_to_schema(e) for e in subgraph.edges],
    )


class GraphService:
    """Business logic for the knowledge-graph API."""

    def __init__(self, store) -> None:
        self._store = store

    async def get_entity(self, entity_id: str) -> GraphNodeSchema:
        node = await self._store.get_entity(entity_id)
        if node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found in graph"
            )
        return _node_to_schema(node)

    async def get_relationships(self, entity_id: str) -> list[GraphEdgeSchema]:
        edges = await self._store.get_relationships(entity_id)
        return [_edge_to_schema(e) for e in edges]

    async def get_neighbors(
        self,
        entity_id: str,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
    ) -> list[GraphNodeSchema]:
        nodes = await self._store.get_neighbors(entity_id, node_types=node_types, rel_types=rel_types)
        return [_node_to_schema(n) for n in nodes]

    async def expand(
        self,
        entity_id: str,
        depth: int = 1,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
    ) -> GraphResponse:
        subgraph = await self._store.expand_neighborhood(
            entity_id, depth=depth, node_types=node_types, rel_types=rel_types
        )
        return _subgraph_to_response(subgraph)

    async def build_network(
        self,
        node_types: list[str] | None = None,
        rel_types: list[str] | None = None,
        limit: int = 500,
    ) -> GraphResponse:
        subgraph = await self._store.build_network(
            node_types=node_types, rel_types=rel_types, limit=limit
        )
        return _subgraph_to_response(subgraph)
