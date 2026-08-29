"""Temporal + location analysis tests (original Phase 9)."""
from app.analysis import location as loc
from app.analysis import temporal as tm
from app.ingestion.generator import generate_synthetic, SCENARIO_COMM_ANOMALY, SCENARIO_NORMAL
from app.services.analysis_service import TemporalLocationService


def test_time_windows_buckets():
    records = generate_synthetic(SCENARIO_NORMAL)
    windows = tm.time_windows(records, minutes=60)
    assert len(windows) >= 1
    total = sum(len(items) for _, items in windows)
    assert total == len(records)


def test_event_sequences_sorted_and_filtered():
    records = generate_synthetic(SCENARIO_NORMAL)
    seq = tm.event_sequences(records, entity_id="P-0421")
    assert seq
    # Chronological
    timestamps = [e["timestamp"] for e in seq]
    assert timestamps == sorted(timestamps)


def test_communication_bursts_detected_on_anomaly():
    records = generate_synthetic(SCENARIO_COMM_ANOMALY)
    bursts = tm.communication_bursts(records)
    assert any(b["count"] >= 2 for b in bursts)


def test_location_activity_ranks_hotspots():
    records = generate_synthetic(SCENARIO_NORMAL)
    activity = loc.location_activity(records)
    assert activity
    events = [a["events"] for a in activity]
    assert events == sorted(events, reverse=True)
    assert all(a["level"] in {"LOW", "MEDIUM", "HIGH"} for a in activity)


def test_movement_sequences_of_entity():
    records = generate_synthetic(SCENARIO_NORMAL)
    movement = loc.movement_sequences(records, entity_id="P-0421")
    assert isinstance(movement, list)


def test_time_filter_inclusive():
    records = generate_synthetic(SCENARIO_NORMAL)
    filtered = loc.time_filter(records, start="2026-08-11T00:00", end="2026-08-12T23:59")
    assert all("2026-08-1" in r.timestamp or "2026-08-2" in r.timestamp for r in filtered)


def test_service_analyze_scenario_returns_response():
    service = TemporalLocationService()
    response = service.analyze_scenario(SCENARIO_NORMAL)
    assert response.windows
    assert response.event_sequence
