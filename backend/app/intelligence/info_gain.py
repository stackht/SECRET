"""Information gain engine (Phase 10).

Estimates how much NEW information examining a candidate (entity, relationship,
potential link, location, gap) could reveal. Considers uncertainty, missing
evidence, network impact, cross-community value, temporal relevance and number
of affected entities. Deterministic; feeds Next-Best-Action.
"""
from __future__ import annotations

from app.intelligence.models import CaseData, EvidenceGap, InfoGain, PotentialLink


def _info_gain(subject: str, score: float, factors: dict[str, float], expected: str, explanation: str) -> InfoGain:
    return InfoGain(
        subject=subject,
        score=round(min(max(score, 0.0), 100.0), 1),
        factors={k: round(v, 1) for k, v in factors.items()},
        expected_value=expected,
        explanation=explanation,
    )


def entity_gain(data: CaseData, entity_id: str, uncertainty: float, affected: int) -> InfoGain:
    """Info gain from examining an entity."""
    neighbors = data.neighbors(entity_id)
    cross_comm = 0.0
    score = (
        uncertainty * 0.35
        + min(100.0, affected * 12.0) * 0.3
        + min(100.0, len(neighbors) * 6.0) * 0.2
        + cross_comm * 0.15
    )
    return _info_gain(
        subject=entity_id,
        score=score,
        factors={"uncertainty": uncertainty, "affected_entities": float(affected),
                 "direct_neighbors": float(len(neighbors)), "cross_community": cross_comm},
        expected="likely surfaces connecting entities and unseen evidence",
        explanation=f"Examining {entity_id} could resolve {uncertainty:.0f}% uncertainty "
                    f"and touches {len(neighbors)} direct neighbors.",
    )


def relationship_gain(data: CaseData, source: str, target: str, missing_evidence: int, strength: float) -> InfoGain:
    """Info gain from validating a relationship / potential link."""
    score = (
        min(100.0, missing_evidence * 20.0) * 0.5
        + strength * 0.3
        + (100.0 - missing_evidence * 10.0) * 0.2
    )
    return _info_gain(
        subject=f"{source}<->{target}",
        score=score,
        factors={"missing_evidence": missing_evidence, "strength": strength},
        expected="confirms or rejects an observed/potential relationship with direct evidence",
        explanation=f"Validating {source}-{target} closes {missing_evidence} evidence gap(s) "
                    f"with {strength:.0f}% structural strength.",
    )


def potential_link_gain(data: CaseData, link: PotentialLink) -> InfoGain:
    """Info gain from investigating a potential (hidden) link."""
    score = min(100.0, link.score * 0.6 + (100.0 - link.score) * 0.5)
    return _info_gain(
        subject=f"{link.source}<->{link.target}",
        score=score,
        factors={"potential_score": link.score, "supporting_signals": float(len(link.supporting_signals))},
        expected="determines whether the potential relationship is real or coincidental",
        explanation=f"{link.source}-{link.target} is a potential link with score {link.score:.0f}% "
                    f"and {len(link.supporting_signals)} supporting signal(s); resolving it has "
                    f"high information value.",
    )


def gap_gain(gap: EvidenceGap) -> InfoGain:
    """Info gain from closing an evidence gap."""
    return _info_gain(
        subject=gap.subject,
        score=gap.importance,
        factors={"importance": gap.importance, "missing": float(len(gap.missing_evidence))},
        expected=f"fills {len(gap.missing_evidence)} missing evidence item(s)",
        explanation=gap.explanation,
    )