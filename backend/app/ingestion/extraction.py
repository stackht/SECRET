"""Entity + relationship extraction (original Phase 4).

Deterministic extraction from normalized `SourceRecord`s into entity mentions and
relationship mentions. Uses the structured fields carried by the synthetic
records (the stand-in for an NLP pipeline on real free-text sources). SharePoint
keys and signal words let clearer extraction grow in later phases.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.ingestion.records import SourceRecord

# entity kind -> relationship type(s) derived from the record's semantics.
_REL_BY_FIELD: dict[str, list[tuple[str, str, str]]] = {
    # (entity field A, entity field B, relationship type)
    "person": [("org", "member_of")],
    "owner": [("vehicle", "owns")],
    "vehicle": [("owner", "owned_by")],
    "caller_phone": [("receiver_phone", "called")],
    "receiver_phone": [("caller_phone", "received_call")],
    "sender": [("receiver", "transferred_to")],
}


@dataclass
class EntityMention:
    entity_id: str
    entity_type: str
    name: str
    confidence: float


@dataclass
class RelationshipMention:
    source_id: str
    target_id: str
    rel_type: str
    confidence: float
    timestamp: str = ""
    attributes: dict = field(default_factory=dict)


@dataclass
class ExtractionResult:
    entities: list[EntityMention] = field(default_factory=list)
    relationships: list[RelationshipMention] = field(default_factory=list)


# Map record field names appearing in our synthetic records to entity types + names.
_FIELD_ENTITIES: dict[str, tuple[str, str]] = {
    "person": ("PERSON", "Person A"),
    "org": ("ORGANIZATION", "Organization Orion"),
    "vehicle": ("VEHICLE", "Vehicle"),
    "owner": ("PERSON", "Owner"),
    "location": ("LOCATION", "Location"),
    "caller_phone": ("PHONE", "Phone"),
    "receiver_phone": ("PHONE", "Phone"),
    "sender": ("ACCOUNT", "Account"),
    "receiver": ("ACCOUNT", "Account"),
}


def extract(record: SourceRecord) -> ExtractionResult:
    """Extract entity + relationship mentions from a normalized record."""
    result = ExtractionResult()
    fields = record.fields or {}

    # Entity mentions from known structured fields.
    for key, (etype, default_name) in _FIELD_ENTITIES.items():
        value = fields.get(key)
        if value is None:
            continue
        if isinstance(value, (list,)):
            continue
        entity_id = str(value)
        name = default_name if key == "person" else entity_id
        result.entities.append(
            EntityMention(entity_id=entity_id, entity_type=etype, name=name, confidence=0.9)
        )

    # Relationship mentions.
    for a_field, pairs in _REL_BY_FIELD.items():
        a_value = fields.get(a_field)
        if a_value is None:
            continue
        for b_field, rel_type in pairs:
            b_value = fields.get(b_field)
            if b_value is None:
                continue
            attrs = {k: fields[k] for k in ("amount", "duration") if fields.get(k)}
            result.relationships.append(
                RelationshipMention(
                    source_id=str(a_value),
                    target_id=str(b_value),
                    rel_type=rel_type,
                    confidence=0.85,
                    timestamp=record.timestamp,
                    attributes=attrs,
                )
            )

    return result


def extract_many(records: list[SourceRecord]) -> ExtractionResult:
    """Extract across many records, merging entity mentions."""
    merged = ExtractionResult()
    seen_entities: set[tuple[str, str]] = set()
    for record in records:
        res = extract(record)
        for e in res.entities:
            key = (e.entity_id, e.entity_type)
            if key not in seen_entities:
                seen_entities.add(key)
                merged.entities.append(e)
        merged.relationships.extend(res.relationships)
    return merged
