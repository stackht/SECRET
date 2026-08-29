"""Temporal analysis (original Phase 9).

Correlates events by time: window bucketing, per-entity sequences, communication
bursts, and transaction sequences. Never asserts causality from correlation.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from app.ingestion.records import CDR, TRANSACTION, SourceRecord


def _parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def sort_by_time(records: list[SourceRecord]) -> list[SourceRecord]:
    """Return records sorted chronologically (stable for missing timestamps)."""
    return sorted(records, key=lambda r: (_parse_ts(r.timestamp) or datetime.min))


def time_windows(records: list[SourceRecord], minutes: int = 60) -> list[tuple[str, list[SourceRecord]]]:
    """Bucket records into `minutes`-sized windows keyed by window start (ISO-HH:MM)."""
    buckets: dict[str, list[SourceRecord]] = defaultdict(list)
    for record in sort_by_time(records):
        ts = _parse_ts(record.timestamp)
        if ts is None:
            buckets["unknown"].append(record)
            continue
        floor = ts - timedelta(minutes=ts.minute % minutes, seconds=ts.second, microseconds=ts.microsecond)
        buckets[floor.strftime("%Y-%m-%dT%H:%M")].append(record)
    return list(buckets.items())


def event_sequences(
    records: list[SourceRecord], entity_id: str | None = None, limit: int = 200
) -> list[dict[str, Any]]:
    """Return chronological events, optionally filtered to an entity."""
    seq: list[dict[str, Any]] = []
    for record in sort_by_time(records):
        if entity_id is not None and not _mentions_entity(record, entity_id):
            continue
        seq.append(
            {
                "record_id": record.record_id,
                "timestamp": record.timestamp,
                "source": record.source_type,
                "summary": record.text[:160],
                "location": record.fields.get("location"),
            }
        )
        if len(seq) >= limit:
            break
    return seq


def _mentions_entity(record: SourceRecord, entity_id: str) -> bool:
    return any(str(v) == entity_id for k, v in (record.fields or {}).items() if isinstance(v, (str, int)))


def communication_bursts(records: list[SourceRecord], gap_minutes: int = 5) -> list[dict[str, Any]]:
    """Detect time clusters of communication events (possible coordination bursts)."""
    comm = [r for r in records if r.source_type == CDR]
    comm = sort_by_time(comm)
    bursts: list[dict[str, Any]] = []
    if not comm:
        return bursts
    current_start = _parse_ts(comm[0].timestamp) or datetime.min
    current_count = 0
    for record in comm:
        ts = _parse_ts(record.timestamp) or datetime.min
        if ts - current_start <= timedelta(minutes=gap_minutes):
            current_count += 1
        else:
            if current_count >= 2:
                bursts.append({"window_start": current_start.isoformat(), "count": current_count})
            current_start = ts
            current_count = 1
    bursts.append({"window_start": current_start.isoformat(), "count": current_count})
    return [b for b in bursts if b["count"] >= 2]


def transaction_sequences(records: list[SourceRecord], max_chain: int = 10) -> list[dict[str, Any]]:
    """Return temporal chain of financial transfers (sender->receiver in time order)."""
    tx = [r for r in records if r.source_type == TRANSACTION]
    tx = sort_by_time(tx)
    return [
        {
            "record_id": r.record_id,
            "timestamp": r.timestamp,
            "sender": r.fields.get("sender"),
            "receiver": r.fields.get("receiver"),
            "amount": r.fields.get("amount"),
        }
        for r in tx[:max_chain]
    ]
