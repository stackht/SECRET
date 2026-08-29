"""Hidden link prediction (Phase 8).

Scores non-observed node pairs by structural similarity (Adamic-Adar, Jaccard,
common neighbors) to suggest possible hidden relationships. Analytical only —
offers candidates, never asserts a fact.
"""
from __future__ import annotations

from itertools import combinations

import networkx as nx


def _adamic_adar(graph: nx.Graph) -> dict[tuple[str, str], float]:
    return nx.adamic_adar_index(graph)


def _jaccard(graph: nx.Graph) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for a, b, score in nx.jaccard_coefficient(graph):
        out[(a, b)] = float(score)
    return out


def predict_links(graph: nx.Graph, top_k: int = 20) -> list[dict]:
    """Return top candidate (non-edge) pairs with a link-prediction score 0..1.

    Adamic-Adar is used as the primary signal (good balance of precision and
    interpretability); Jaccard is provided as a strength indicator.
    """
    if graph.number_of_nodes() < 2:
        return []

    try:
        aa = dict(_adamic_adar(graph))
    except Exception:  # noqa: BLE001
        aa = {}
    try:
        jac = _jaccard(graph)
    except Exception:  # noqa: BLE001
        jac = {}

    # Normalize Adamic-Adar scores to 0..1 across candidates.
    if aa:
        mx = max(abs(v) for v in aa.values()) or 1.0
        aa = {k: abs(v) / mx for k, v in aa.items()}

    candidates: dict[tuple[str, str], float] = {}
    for (a, b), score in aa.items():
        if graph.has_edge(a, b):
            continue
        combined = 0.7 * score + 0.3 * jac.get((a, b), 0.0)
        candidates[(a, b)] = combined

    ranked = sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [
        {"source": a, "target": b, "score": round(score * 100.0, 1)}
        for (a, b), score in ranked
    ]
