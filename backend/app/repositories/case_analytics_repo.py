"""Build intelligence CaseData from persisted case records (Phase 14).

Reads a case's entities, relationships and source records and maps them into
the engine's typed input (EntityData / RelData / Evidence), carrying
provenance, temporal envelope and amounts so every downstream engine has what
it needs.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.fusion import SOURCE_RELIABILITY
from app.intelligence.models import CaseData, EntityData, Evidence, RelData
from app.repositories.entity_repository import EntityRepository, RelationshipRepository
from app.repositories.source_repository import SourceRepository

# Relaxation: normalize rel type to upper for consistency.
_COMM_REL = ("CALLED", "MESSAGED")
_TX_REL = ("TRANSFERRED_TO",)


async def build_case_data(session: AsyncSession, case_id: int) -> CaseData:
    entities = await EntityRepository(session).list_by_case(case_id)
    relationships = await RelationshipRepository(session).list_by_case(case_id)
    sources = await SourceRepository(session).list_by_case(case_id)

    entity_data = [
        EntityData(
            id=e.entity_id,
            type=e.entity_type,
            name=e.name,
            aliases=[],
            source_ids=e.source_ids or [],
            metadata=e.attributes or {},
        )
        for e in entities
    ]

    rel_data: list[RelData] = []
    for r in relationships:
        attrs = r.attributes or {}
        amount = attrs.get("amount")
        try:
            amount = float(amount) if amount else 0.0
        except (TypeError, ValueError):
            amount = 0.0
        strength = min(1.0, float(attrs.get("count") or r.confidence))
        rel_data.append(
            RelData(
                source=r.source_id,
                target=r.target_id,
                rel_type=r.rel_type.upper(),
                confidence=r.confidence,
                source_ids=r.source_ids or [],
                first_seen=str(attrs.get("first_seen") or ""),
                last_seen=str(attrs.get("last_seen") or ""),
                count=int(attrs.get("count") or 1),
                timestamps=[str(t) for t in (attrs.get("timestamps") or [])],
                amount=amount,
                strength=min(1.0, strength),
            )
        )

    evidence: list[Evidence] = []
    for source in sources:
        meta = source.metadata_json or {}
        reliability = SOURCE_RELIABILITY.get(source.source_type or "OTHER", 0.5)
        text = str(meta.get("text") or "")
        if text:
            evidence.append(
                Evidence(
                    id=source.source_id,
                    source_type=source.source_type or "OTHER",
                    source_id=source.source_id,
                    timestamp="",
                    entity_ids=[],
                    summary=text[:200],
                    reliability=reliability,
                )
            )
        for rec in meta.get("records") or []:
            fields = rec.get("fields") or {}
            entity_ids = [
                str(v) for v in (
                    fields.get("caller_phone"), fields.get("receiver_phone"),
                    fields.get("sender"), fields.get("receiver"),
                    fields.get("vehicle"), fields.get("owner"),
                    fields.get("entity"), fields.get("location"),
                ) if v
            ]
            evidence.append(
                Evidence(
                    id=f"{source.source_id}:{rec.get('id') or ''}",
                    source_type=source.source_type or "OTHER",
                    source_id=source.source_id,
                    timestamp=str(rec.get("timestamp") or ""),
                    entity_ids=entity_ids,
                    summary=str(rec.get("text") or "")[:200],
                    reliability=reliability,
                )
            )

    # Deduplicate evidence ids.
    seen: set[str] = set()
    unique_evidence: list[Evidence] = []
    for e in evidence:
        if e.id in seen:
            continue
        seen.add(e.id)
        unique_evidence.append(e)

    return CaseData(
        case_number="",
        entities=entity_data,
        relationships=rel_data,
        evidence=unique_evidence,
    )