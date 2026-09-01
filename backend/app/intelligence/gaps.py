"""Evidence gap engine (Phase 7).

Identifies what evidence is MISSING to strengthen or reject an investigative
hypothesis. For each potential relationship or low-coverage entity, reports
known evidence, missing evidence, importance, recommended data source, and an
explanation. Feeds the Next-Best-Action engine.
"""
from __future__ import annotations

from app.intelligence.models import CaseData, EvidenceGap, PotentialLink

# Recommended source to close each gap type, with a suggested review window.
_SOURCE_FOR_GAP = {
    "direct_communication": ("CDR", "review inbound/outbound call and message records"),
    "independent_source": ("LOCATION", "independent geospatial or surveillance observation"),
    "financial_confirmation": ("TRANSACTION", "bank transaction records between parties"),
    "vehicle_association": ("VEHICLE", "vehicle registration and movement logs"),
    "documentary": ("FIR", "police report or documentary record"),
}


def gaps_for_potential_links(data: CaseData, links: list[PotentialLink], top_k: int = 8) -> list[EvidenceGap]:
    """Derive evidence gaps for the strongest potential relationships."""
    gaps: list[EvidenceGap] = []
    for link in links[:top_k]:
        known: list[str] = list(link.supporting_signals)
        missing: list[str] = []
        # No direct communication edge => communication evidence missing.
        has_direct = any(
            (r.source == link.source and r.target == link.target)
            or (r.source == link.target and r.target == link.source)
            for r in data.relationships
        )
        if not has_direct:
            missing.append("direct communication or transfer evidence")
        # Only one source type supporting => weak independent confirmation.
        src_types = {e.source_type for e in data.evidence if link.source in e.entity_ids or link.target in e.entity_ids}
        if len(src_types) < 2:
            missing.append("independent confirmation from a second source type")
        if not missing:
            continue
        rec_src, window = _recommend_for_missing(missing)
        importance = link.score
        gaps.append(
            EvidenceGap(
                subject=f"{link.source}<->{link.target}",
                known_evidence=known,
                missing_evidence=missing,
                importance=round(importance, 1),
                recommended_source=rec_src,
                window=window,
                explanation=(
                    f"Before accepting {link.source}-{link.target} as a link, obtain: "
                    f"{'; '.join(missing)}. This would raise the evidence confidence for the "
                    f"potential relationship."
                ),
            )
        )
    return gaps


def gaps_for_low_coverage(data: CaseData, min_sources: int = 1, top_k: int = 8) -> list[EvidenceGap]:
    """Flag entities appearing in too few independent source types."""
    source_count: dict[str, set[str]] = {}
    for e in data.evidence:
        for entity in e.entity_ids:
            source_count.setdefault(entity, set()).add(e.source_type)

    gaps: list[EvidenceGap] = []
    for entity in data.entities:
        types = source_count.get(entity.id, set())
        if len(types) <= min_sources:
            rec_src, window = "CDR", "a 14-day observation window"
            gaps.append(
                EvidenceGap(
                    subject=entity.id,
                    known_evidence=[f"{entity.type} {entity.id} appears in {len(types)} source type(s)"]
                                    if types else [f"{entity.type} {entity.id} has no recorded evidence"],
                    missing_evidence=["independent corroboration across source types"],
                    importance=round(40.0 + len(types) * 10.0, 1),
                    recommended_source=rec_src,
                    window=window,
                    explanation=f"{entity.id} is under-connected in the evidence record; "
                                f"more source coverage would clarify its role.",
                )
            )
            if len(gaps) >= top_k:
                break
    return gaps


def _recommend_for_missing(missing: list[str]) -> tuple[str, str]:
    for m in missing:
        for key, (src, desc) in _SOURCE_FOR_GAP.items():
            if key in m:
                return src, desc
    return "CDR", "a 14-day observation window"