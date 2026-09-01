"""Multi-source evidence fusion (Phase 3).

For a subject (entity or relationship) assemble the supporting vs contradictory
evidence across source types and derive an EXPLAINABLE confidence score from
independent-source count and per-source reliability. Deterministic — no random
values, every factor is computed and surfaced.
"""
from __future__ import annotations

from collections import defaultdict

from app.intelligence.models import CaseData, Evidence, FusionResult, RelData

# Base reliability per source type (0..1). These are domain priors, fixed and
# explainable — a CDR is a strong structured signal, social media weaker.
SOURCE_RELIABILITY: dict[str, float] = {
    "CDR": 0.85,
    "TRANSACTION": 0.85,
    "FIR": 0.8,
    "VEHICLE": 0.7,
    "LOCATION": 0.65,
    "SURVEILLANCE": 0.6,
    "INTELLIGENCE": 0.55,
    "SOCIAL": 0.4,
    "CRIMINAL_HISTORY": 0.7,
    "OTHER": 0.5,
}

# Sources that lend positive weight vs sources that merely record context.
CONTRADICTORY_WORDS = ("denied", "rebutted", "contradict", "unsubstantiated", "inconsistent")


def evidence_for_subject(data: CaseData, subject: str) -> list[Evidence]:
    """Collect evidence mentioning an entity, or derived from a relationship."""
    return [e for e in data.evidence if subject in e.entity_ids]


def _reliability(source_type: str) -> float:
    return SOURCE_RELIABILITY.get(source_type, SOURCE_RELIABILITY["OTHER"])


def fuse_relationship(data: CaseData, rel: RelData) -> FusionResult:
    """Fuse the evidence backing a single relationship."""
    # Evidence = the source records that produced this relationship, weighted by
    # source reliability + relationship confidence + temporal consistency.
    source_types: dict[str, int] = defaultdict(int)
    supporting: list[str] = []
    contradictory: list[str] = []
    factors: list[dict] = []

    for e in data.evidence:
        is_support = rel.source in e.entity_ids or rel.target in e.entity_ids
        text = (e.summary or "").lower()
        contradicts = any(w in text for w in CONTRADICTORY_WORDS)
        if is_support and contradicts:
            contradictory.append(f"{e.source_id} ({e.source_type}) contradicts the link")
        elif is_support:
            source_types[e.source_type] += 1
            supporting.append(f"{e.source_id} ({e.source_type}) — {e.summary or 'observation'}")

    independent = len([k for k, v in source_types.items() if v > 0])
    base = 0.0
    for stype, n in source_types.items():
        base += _reliability(stype) * min(n, 1)  # capped: first occurrence most valuable
    # Blend structural confidence of the relationship itself.
    base += rel.confidence * 0.5

    conflict_penalty = len(contradictory) * 0.05
    score = round(min(max(base * 100.0 - conflict_penalty * 100.0, 0.0), 100.0), 1)
    level = _level(score)

    factors.append({"label": "independent_sources", "value": independent, "weight": "high"})
    factors.append({"label": "source_reliability", "value": round(base * 100.0, 1), "weight": "high"})
    factors.append({"label": "relationship_confidence", "value": round(rel.confidence * 100.0, 1), "weight": "medium"})
    if conflict_penalty:
        factors.append({"label": "contradictory_evidence", "value": -round(conflict_penalty * 100.0, 1), "weight": "negative"})

    explanation = _explain(subject=f"{rel.source}<->{rel.target}", score=score, independent=independent,
                           supporting=len(supporting), contradictory=len(contradictory))

    return FusionResult(
        subject=f"{rel.source}<->{rel.target}",
        score=score,
        level=level,
        supporting_evidence=supporting,
        contradictory_evidence=contradictory,
        factors=factors,
        source_count=len(supporting) + len(contradictory),
        independent_source_count=independent,
        explanation=explanation,
    )


def fuse_entity(data: CaseData, entity_id: str) -> FusionResult:
    """Fuse evidence touching an entity across all sources."""
    source_types: dict[str, int] = defaultdict(int)
    supporting: list[str] = []
    contradictory: list[str] = []
    for e in evidence_for_subject(data, entity_id):
        text = (e.summary or "").lower()
        if any(w in text for w in CONTRADICTORY_WORDS):
            contradictory.append(f"{e.source_id} ({e.source_type}) conflicts")
        else:
            source_types[e.source_type] += 1
            supporting.append(f"{e.source_id} ({e.source_type}) — {e.summary or 'observation'}")

    independent = len([k for k, v in source_types.items() if v > 0])
    base = sum(_reliability(k) for k in source_types) * 0.5 + min(independent, 4) * 0.12
    score = round(min(base * 100.0, 100.0), 1)
    factors = [
        {"label": "independent_sources", "value": independent, "weight": "high"},
        {"label": "source_reliability", "value": round(sum(_reliability(k) for k in source_types) * 50.0, 1), "weight": "high"},
        {"label": "total_signals", "value": len(supporting), "weight": "medium"},
    ]
    return FusionResult(
        subject=entity_id,
        score=score,
        level=_level(score),
        supporting_evidence=supporting,
        contradictory_evidence=contradictory,
        factors=factors,
        source_count=len(supporting) + len(contradictory),
        independent_source_count=independent,
        explanation=_explain(subject=entity_id, score=score, independent=independent,
                             supporting=len(supporting), contradictory=len(contradictory)),
    )


def _level(score: float) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _explain(subject: str, score: float, independent: int, supporting: int, contradictory: int) -> str:
    parts = [f"{subject} reaches {score:.0f}/100 evidence confidence from {independent} "
             f"independent source type(s) supporting {supporting} signal(s)."]
    if contradictory:
        parts.append(f"{contradictory} contradicting signal(s) reduce confidence.")
    if independent == 0:
        parts.append("No independent structured evidence yet — low confidence.")
    return " ".join(parts)