"""Centrality metrics (Phase 8)."""
from __future__ import annotations

import networkx as nx


def degree_centrality(graph: nx.Graph) -> dict[str, float]:
    """Return normalized degree centrality for every node."""
    return nx.degree_centrality(graph)


def betweenness_centrality(graph: nx.Graph) -> dict[str, float]:
    """Return normalized betweenness centrality."""
    return nx.betweenness_centrality(graph)


def closeness_centrality(graph: nx.Graph) -> dict[str, float]:
    """Return normalized closeness centrality (skips unreachable components)."""
    return nx.closeness_centrality(graph)


def pagerank(graph: nx.Graph) -> dict[str, float]:
    """Return PageRank scores for every node."""
    if graph.number_of_nodes() == 0:
        return {}
    try:
        return nx.pagerank(graph, weight="weight")
    except nx.PowerIterationFailedConvergence:
        return nx.pagerank(graph, weight="weight", max_iter=500, tol=1e-4)


def composite_importance(graph: nx.Graph) -> dict[str, float]:
    """Combine PageRank + degree + betweenness into a single 0..1 importance score."""
    nodes = list(graph.nodes())
    if not nodes:
        return {}

    pr = pagerank(graph)
    deg = degree_centrality(graph)
    betw = betweenness_centrality(graph)

    def _norm(values: dict[str, float]) -> dict[str, float]:
        mx = max(values.values(), default=0.0)
        if mx <= 0:
            return {k: 0.0 for k in nodes}
        return {k: v / mx for k, v in values.items()}

    pr_n, deg_n, betw_n = _norm(pr), _norm(deg), _norm(betw)
    return {
        node: 0.5 * pr_n[node] + 0.3 * deg_n[node] + 0.2 * betw_n[node]
        for node in nodes
    }
