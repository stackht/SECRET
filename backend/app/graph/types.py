"""Domain types for the knowledge graph (Phase 6).

These are store-agnostic: used by both the Neo4j and in-memory implementations
so the rest of the application does not depend on graph-impl specifics.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphNode:
    """A single entity node in the knowledge graph."""

    id: str                     # stable identifier, e.g. P-0421
    type: str                   # PERSON | ORGANIZATION | PHONE | ...
    name: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """A single typed relationship edge between two nodes."""

    id: str
    source_id: str              # tail node id
    target_id: str              # head node id
    type: str                   # OWNS | USES | MEMBER_OF | ...
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphSubgraph:
    """A set of nodes and edges returned from a query (e.g. neighborhood)."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
