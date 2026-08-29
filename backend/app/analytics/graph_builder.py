"""Builds an undirected NetworkX graph from GraphStore data (Phase 8).

The analytics modules operate on a NetworkX graph for algorithm availability and
simplicity, decoupled from the underlying Neo4j/in-memory store.
"""
import networkx as nx

from app.graph.types import GraphSubgraph


def build_graph(subgraph: GraphSubgraph) -> nx.Graph:
    """Return an undirected graph from nodes/edges.

    Node attributes from `GraphNode.properties` are copied onto the NetworkX
    nodes so downstream analytics (e.g. risk scoring) can read entity metadata.
    """
    graph = nx.Graph()
    for node in subgraph.nodes:
        attrs: dict = {"type": node.type, "name": node.name, **node.properties}
        graph.add_node(node.id, **attrs)
    for edge in subgraph.edges:
        weight = float(edge.properties.get("weight", edge.properties.get("confidence", 1.0)) or 1.0)
        data: dict = {"type": edge.type, "weight": weight}
        if graph.has_edge(edge.source_id, edge.target_id):
            # Avoid overwriting; add type as a list on parallel edges.
            existing = data.get("type")
            data["type"] = [existing, edge.type]
        graph.add_edge(edge.source_id, edge.target_id, **data)
    return graph
