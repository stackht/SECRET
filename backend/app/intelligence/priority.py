"""Investigation priority engine (Phase 9).

Ranks entities and relationships by INVESTIGATIVE VALUE using an explainable
deterministic weighted blend of centrality, bridge importance, anomaly, temporal
relevance, evidence relevance, uncertainty and cross-community impact.
Weights are configurable. Terminology is investigation priority — never guilt.
"""
from __future__ import annotations

from app.intelligence.models import CaseData, PriorityScore

# Default priority weights (0..1 each). Restructuring-risk ceiling.
DEFAULT_WEIGHTS = {
    "centrality": 0.20,
    "bridge_importance": 0.15,
    "anomaly": 0.15,
    "temporal_relevance": 0.15,
    "evidence_relevance": 0.15,
    "uncertainty": 0.10,
    "cross_community_impact": 0.10,
}

_MAX = {
    "centrality": 100.0,
    "bridge_importance": 100.0,
    "anomaly": 100.0,
    "temporal_relevance": 100.0,
    "evidence_relevance": 100.0,
    "uncertainty": 100.0,
    "cross_community_impact": 100.0,
}

_FACTOR_LABELS = {
    "centrality": "Network importance",
    "bridge_importance": "Network bridge",
    "anomaly": "Anomaly signal",
    "temporal_relevance": "Recent activity",
    "evidence_relevance": "Evidence relevance",
    "uncertainty": "Uncertainty",
    "cross_community_impact": "Cross-community impact",
}


def _score(subject: str, factors: dict[str, float], weights: dict[str, float]) -> PriorityScore:
    total = sum(weights.get(k, 0.0) * (min(max(v, 0.0), _MAX[k]) / _MAX[k]) for k, v in factors.items())
    priority = round(total * 100.0, 1)
    explanation = []
    ordered = sorted(factors.items(), key=lambda kv: weights.get(kv[0], 0.0), reverse=True)
    for k, v in ordered:
        contribution = round(weights.get(k, 0.0) * (min(max(v, 0.0), _MAX[k]) / _MAX[k]) * 100.0, 0)
        if contribution > 0:
            explanation.append(f"{_FACTOR_LABELS.get(k, k)}: +{contribution:.0f}")
    return PriorityScore(subject=subject, priority=priority, factors=factors, explanation=explanation)


def score_entity(
    entity_id: str,
    degree_c: float,
    betweenness_c: float,
    community_count: int,
    anomaly_score: float,
    recent_activity: float,
    evidence_score: float,
    source_count: int,
    weights: dict[str, float] | None = None,
) -> PriorityScore:
    """Score a single entity."""
    weights = weights or DEFAULT_WEIGHTS
    factors = {
        "centrality": round(degree_c * 100.0, 1),
        "bridge_importance": round(betweenness_c * 100.0, 1),
        "anomaly": anomaly_score,
        "temporal_relevance": recent_activity,
        "evidence_relevance": evidence_score,
        "uncertainty": round(100.0 - min(100.0, source_count * 20.0), 1),
        "cross_community_impact": round(min(100.0, community_count * 20.0), 1),
    }
    return _score(entity_id, factors, weights)


def score_relationship(
    subject: str,
    strength: float,
    anomaly_score: float,
    evidence_score: float,
    cross_community: int,
    source_count: int,
    weights: dict[str, float] | None = None,
) -> PriorityScore:
    """Score a relationship candidate."""
    weights = weights or DEFAULT_WEIGHTS
    factors = {
        "centrality": round(strength * 100.0, 1),
        "bridge_importance": round(0.0, 1),
        "anomaly": anomaly_score,
        "temporal_relevance": round(strength * 100.0, 1),
        "evidence_relevance": evidence_score,
        "uncertainty": round(100.0 - min(100.0, source_count * 20.0), 1),
        "cross_community_impact": round(min(100.0, cross_community * 25.0), 1),
    }
    return _score(subject, factors, weights)


def rank_entities(data: CaseData, centrality: dict[str, float], betweenness: dict[str, float],
                  communities: list[list[str]], anomalies: dict[str, float],
                  evidence_scores: dict[str, float], source_counts: dict[str, int],
                  weights: dict[str, float] | None = None) -> list[PriorityScore]:
    """Rank all entities by investigation priority."""
    comm_of: dict[str, int] = {}
    for i, members in enumerate(communities):
        for m in members:
            comm_of[m] = comm_of.get(m, 0) + 1  # membership count, not community index

    scored: list[PriorityScore] = []
    for entity in data.entities:
        scored.append(
            score_entity(
                entity.id,
                degree_c=centrality.get(entity.id, 0.0),
                betweenness_c=betweenness.get(entity.id, 0.0),
                community_count=comm_of.get(entity.id, 0),
                anomaly_score=anomalies.get(entity.id, 0.0),
                recent_activity=min(100.0, source_counts.get(entity.id, 0) * 15.0),
                evidence_score=evidence_scores.get(entity.id, 0.0),
                source_count=source_counts.get(entity.id, 0),
                weights=weights,
            )
        )
    scored.sort(key=lambda s: s.priority, reverse=True)
    return scored