"""Risk scoring and anomaly detection (Phase 8).

Risk is an analytical indicator, never a guilt declaration. Combines:
- node-attributed baseline risk (from the knowledge graph / records)
- network-derived signals (degree, isolation, community size)
- optional Isolation Forest anomaly scoring over tabular features
"""
from __future__ import annotations

import networkx as nx

from app.analytics.centrality import degree_centrality, pagerank
from app.analytics.community import detect_communities


def _node_baseline(graph: nx.Graph, node_id: str) -> float:
    props = graph.nodes[node_id]
    baseline = float(props.get("risk_score") or props.get("risk") or 0.0)
    return min(max(baseline, 0.0), 100.0)


def risk_scores(graph: nx.Graph) -> list[dict]:
    """Compute a 0..100 risk score per node from baseline + network signals.

    Signals (each 0..1 then blended):
      - baseline normalized to 0..1
      - degree centrality
      - PageRank
      - isolation penalty (isolated nodes are flagged separately, not punished)
    """
    if graph.number_of_nodes() == 0:
        return []

    deg = degree_centrality(graph)
    pr = pagerank(graph)
    # Community membership size can amplify risk when a node bridges large gang(s).
    comm_of: dict[str, int] = {}
    for community in detect_communities(graph):
        for node in community:
            comm_of[node] = comm_of.get(node, 0) + len(community)

    results: list[dict] = []
    for node_id in graph.nodes():
        baseline = _node_baseline(graph, node_id)
        pr_n = pr.get(node_id, 0.0)
        deg_n = deg.get(node_id, 0.0)
        weight = 0.5 * (baseline / 100.0) + 0.3 * deg_n + 0.2 * pr_n
        score = round(min(max(weight * 100.0, 0.0), 100.0), 1)
        level = _level(score)
        results.append(
            {
                "entity_id": node_id,
                "risk_score": score,
                "risk_level": level,
                "confidence": round(min(100.0, 40.0 + 60.0 * (deg_n + pr_n) / 2.0), 1),
                "indicators": {
                    "baseline": baseline,
                    "degree_centrality": round(deg_n * 100.0, 1),
                    "pagerank": round(pr_n * 100.0, 1),
                    "community_size": comm_of.get(node_id, 0),
                },
            }
        )
    results.sort(key=lambda r: r["risk_score"], reverse=True)
    return results


def _level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def isolation_forest_anomalies(graph: nx.Graph, contamination: float = 0.1) -> list[str]:
    """Return node ids flagged as anomalies by Isolation Forest over network
    feature vectors (degree, pagerank, community size)."""
    try:
        from sklearn.ensemble import IsolationForest
    except Exception:  # noqa: BLE001 - sklearn optional at runtime
        return []

    nodes = list(graph.nodes())
    if len(nodes) < 3:
        return []

    deg = degree_centrality(graph)
    pr = pagerank(graph)
    comm_of: dict[str, int] = {}
    for community in detect_communities(graph):
        for node in community:
            comm_of[node] = max(comm_of.get(node, 0), len(community))

    features = [
        [deg.get(n, 0.0) * 100.0, pr.get(n, 0.0) * 100.0, float(comm_of.get(n, 0))]
        for n in nodes
    ]
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(features)  # -1 = anomaly
    return [n for n, p in zip(nodes, preds) if p == -1]
