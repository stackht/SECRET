"""Next Best Action engine (Phase 11).

Ranks candidate investigative actions (entities, potential links, evidence
gaps, transactions, locations) by priority × information gain, producing
explainable recommendations with WHY, EVIDENCE, EXPECTED VALUE and REQUIRED
DATA. Nothing is hardcoded — every recommendation derives from the other
engines.
"""
from __future__ import annotations

from app.intelligence.models import CaseData, EvidenceGap, InfoGain, PotentialLink, PriorityScore, Recommendation


def build(
    data: CaseData,
    entity_priorities: list[PriorityScore],
    entity_gains: dict[str, InfoGain],
    potential_links: list[PotentialLink],
    link_priorities: list[PriorityScore],
    link_gains: dict[str, InfoGain],
    gaps: list[EvidenceGap],
    top_k: int = 8,
) -> list[Recommendation]:
    """Assemble ranked recommendations across candidates."""
    recs: list[Recommendation] = []

    # High-priority entities.
    for p in entity_priorities[:5]:
        gain = entity_gains.get(p.subject)
        if gain is None:
            continue
        recs.append(
            Recommendation(
                kind="ENTITY",
                subject=p.subject,
                priority=p.priority,
                info_gain=gain.score,
                reasoning=p.explanation,
                entity_ids=[p.subject],
                recommended_data="review all sources mentioning this entity",
                window="last 14 days",
            )
        )

    # Potential hidden links.
    for p in link_priorities[:5]:
        link = next((x for x in potential_links if x.source in p.subject and x.target in p.subject), None)
        gain = link_gains.get(p.subject)
        if gain is None:
            continue
        recs.append(
            Recommendation(
                kind="RELATIONSHIP",
                subject=p.subject,
                priority=p.priority,
                info_gain=gain.score,
                reasoning=p.explanation + (["Potential (unconfirmed) relationship"] if link else []),
                entity_ids=p.subject.replace("<->", "|").split("|"),
                recommended_data="CDR and location records between the pair",
                window="review the relationship before validating",
            )
        )

    # Evidence gaps (information-value closures).
    for gap in gaps[:4]:
        recs.append(
            Recommendation(
                kind="GAP",
                subject=gap.subject,
                priority=gap.importance,
                info_gain=gap.importance,
                reasoning=[gap.explanation],
                recommended_data=gap.recommended_source,
                window=gap.window,
            )
        )

    seen: set[str] = set()
    deduped: list[Recommendation] = []
    for r in recs:
        key = f"{r.kind}:{r.subject}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    deduped.sort(key=lambda r: r.priority + r.info_gain, reverse=True)
    return deduped[:top_k]