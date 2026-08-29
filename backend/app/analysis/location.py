"""Location analysis (original Phase 9).

Location activity, hotspots, movement sequences, and time-range filtering over
source records. Synthetic coordinates only.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.analysis.temporal import sort_by_time
from app.ingestion.records import SourceRecord


def _record_location(record: SourceRecord) -> str | None:
    loc = record.fields.get("location")
    return str(loc) if loc is not None else None


def location_activity(records: list[SourceRecord]) -> list[dict[str, Any]]:
    """Count events per location, sorted by activity (hotspots)."""
    counts: dict[str, int] = {}
    for record in records:
        loc = _record_location(record)
        if loc:
            counts[loc] = counts.get(loc, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [{"location": loc, "events": n, "level": _level(n)} for loc, n in ranked]


def _level(count: int) -> str:
    if count >= 5:
        return "HIGH"
    if count >= 3:
        return "MEDIUM"
    return "LOW"


def movement_sequences(
    records: list[SourceRecord], entity_id: str | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """Chronological movement (location appearances) across records."""
    out: list[dict[str, Any]] = []
    for record in sort_by_time(records):
        if entity_id is not None:
            fields = record.fields or {}
            if not any(str(v) == entity_id for k, v in fields.items() if isinstance(v, (str, int))):
                continue
        loc = _record_location(record)
        if loc is None:
            continue
        out.append(
            {
                "timestamp": record.timestamp,
                "location": loc,
                "source": record.source_type,
                "record_id": record.record_id,
            }
        )
        if len(out) >= limit:
            break
    return out


def time_filter(records: list[SourceRecord], start: str | None = None, end: str | None = None) -> list[SourceRecord]:
    """Filter records by an inclusive timestamp range (ISO)."""
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    result = []
    for record in records:
        try:
            ts = datetime.fromisoformat(record.timestamp)
        except (ValueError, TypeError):
            continue
        if start_dt and ts < start_dt:
            continue
        if end_dt and ts > end_dt:
            continue
        result.append(record)
    return result


def activity_clusters(records: list[SourceRecord]) -> dict[str, list[str]]:
    """Group locations by activity level (LOW/MEDIUM/HIGH)."""
    buckets: dict[str, list[str]] = {"LOW": [], "MEDIUM": [], "HIGH": []}
    for entry in location_activity(records):
        buckets[entry["level"]].append(entry["location"])
    return buckets
