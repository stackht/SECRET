"""Graph API schemas (Phase 6)."""
from pydantic import BaseModel, Field


class GraphNodeSchema(BaseModel):
    """Serialized representation of a graph node."""

    id: str
    type: str
    name: str
    properties: dict = Field(default_factory=dict)


class GraphEdgeSchema(BaseModel):
    """Serialized representation of a typed relationship edge."""

    id: str
    source: str
    target: str
    type: str
    properties: dict = Field(default_factory=dict)


class GraphResponse(BaseModel):
    """A slice of the knowledge graph (nodes + edges)."""

    nodes: list[GraphNodeSchema] = Field(default_factory=list)
    edges: list[GraphEdgeSchema] = Field(default_factory=list)
