"""Community (gang) detection and network-level metrics (Phase 8)."""
from __future__ import annotations

import networkx as nx
from networkx.algorithms.community import louvain_communities


def detect_communities(graph: nx.Graph, resolution: float = 1.0) -> list[list[str]]:
    """Return communities as lists of node ids using the Louvain algorithm."""
    if graph.number_of_nodes() == 0:
        return []
    try:
        comms = louvain_communities(graph, weight="weight", resolution=resolution, seed=42)
    except Exception:  # noqa: BLE001 - fallback to greedy modularity
        comms = nx.community.greedy_modularity_communities(graph, weight="weight")
    return [list(sorted(c)) for c in comms]


def network_density(graph: nx.Graph) -> float:
    """Return graph density (0..1)."""
    return float(nx.density(graph))


def connected_components(graph: nx.Graph) -> list[list[str]]:
    """Return weakly connected components as lists of node ids."""
    return [list(sorted(c)) for c in nx.connected_components(graph)]


def isolation_levels(graph: nx.Graph) -> list[str]:
    """Return ids of isolated nodes (no edges)."""
    return [n for n, d in graph.degree() if d == 0]
