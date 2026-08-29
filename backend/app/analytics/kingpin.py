"""Kingpin / key-influencer identification (Phase 8).

Ranks entities by composite network importance and marks the top ones as
"key connectors" / potential kingpins. Purely analytical — never a verdict.
"""
from __future__ import annotations

import networkx as nx

from app.analytics.centrality import composite_importance


def rank_key_entities(graph: nx.Graph, top_k: int = 10) -> list[dict]:
    """Return the top-k entities by composite importance, each with its
    composite score and the dominant factor (PageRank / degree / betweenness)."""
    if graph.number_of_nodes() == 0:
        return []

    scores = composite_importance(graph)
    degree = dict(graph.degree())
    degrees = nx.degree_centrality(graph)
    betw = nx.betweenness_centrality(graph)

    ranked: list[dict] = []
    for node_id, score in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
        d = degrees.get(node_id, 0.0)
        b = betw.get(node_id, 0.0)
        p = score  # composite already weights PageRank most heavily
        if p >= d and p >= b:
            factor = "pagerank"
        elif d >= b:
            factor = "degree"
        else:
            factor = "betweenness"
        ranked.append(
            {
                "entity_id": node_id,
                "score": round(score * 100.0, 1),
                "degree": degree.get(node_id, 0),
                "dominant_factor": factor,
            }
        )
        if len(ranked) >= top_k:
            break
    return ranked


def find_bridges(graph: nx.Graph) -> list[str]:
    """Return node ids that are articulation points (bridges between parts)."""
    if graph.number_of_nodes() == 0:
        return []
    try:
        return list(nx.articulation_points(graph))
    except Exception:  # noqa: BLE001 - disconnected graphs may fail; degrade gracefully
        edges = list(nx.bridges(graph))
        nodes: set[str] = set()
        for a, b in edges:
            nodes.add(a)
            nodes.add(b)
        return list(nodes)
