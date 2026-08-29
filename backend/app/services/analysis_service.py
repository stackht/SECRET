"""Temporal + location analysis service (original Phase 9).

Runs temporal + location correlation over a set of source records (from the
synthetic generator or a simulation pipeline) and returns a combined, typed
response consumed by the UI.
"""
from __future__ import annotations

from app.analysis import location as loc
from app.analysis import temporal as tm
from app.ingestion.generator import generate_synthetic
from app.ingestion.records import SourceRecord
from app.schemas.analysis import (
    BurstResult,
    EventSequenceItem,
    LocationActivityEntry,
    TemporalLocationResponse,
    TimeWindowResult,
)


class TemporalLocationService:
    """Correlate a set of source records by time and location."""

    def analyze(self, records: list[SourceRecord], scenario: str = "NORMAL_NETWORK", entity_id: str | None = None) -> TemporalLocationResponse:
        windows = tm.time_windows(records, minutes=60)
        events = tm.event_sequences(records, entity_id=entity_id)
        bursts = tm.communication_bursts(records)
        activity = loc.location_activity(records)
        movement = loc.movement_sequences(records, entity_id=entity_id)

        return TemporalLocationResponse(
            windows=[
                TimeWindowResult(
                    window_start=w,
                    count=len(items),
                    sources=list({r.source_type for r in items}),
                )
                for w, items in windows
            ],
            event_sequence=[
                EventSequenceItem(
                    record_id=e["record_id"],
                    timestamp=e["timestamp"],
                    source=e["source"],
                    summary=e["summary"],
                    location=e["location"],
                )
                for e in events
            ],
            communication_bursts=[BurstResult(window_start=b["window_start"], count=b["count"]) for b in bursts],
            location_activity=[
                LocationActivityEntry(location=a["location"], events=a["events"], level=a["level"])
                for a in activity
            ],
            movement=[
                EventSequenceItem(
                    record_id=m["record_id"],
                    timestamp=m["timestamp"],
                    source=m["source"],
                    summary=m["location"] or "",
                    location=m["location"],
                )
                for m in movement
            ],
        )

    def analyze_scenario(self, scenario: str) -> TemporalLocationResponse:
        """Generate synthetic records for a scenario and analyze them."""
        records = generate_synthetic(scenario)
        return self.analyze(records, scenario=scenario)
