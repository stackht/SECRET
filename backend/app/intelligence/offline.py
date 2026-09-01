"""Offline intelligence builder (Phase 15).

Deterministically synthesizes the same CaseData structure consumed by every
intelligence engine when the backend is offline, so the UI never shows an
empty intelligence experience. Reuses the same canonical identifiers as the
main demo corpus so Network/Location and Intelligence stay coherent.
"""
from __future__ import annotations

from app.intelligence.models import Anomaly, CaseData, EntityData, Evidence, PotentialLink, RelData


def _evidence(source_id: str, source_type: str, summary: str, entity_ids: list[str], reliability: float) -> Evidence:
    return Evidence(id=source_id, source_type=source_type, source_id=source_id, summary=summary,
                    entity_ids=entity_ids, reliability=reliability)


def build_demo_case() -> CaseData:
    """The offline demonstration investigation (Operation Nightfall)."""
    entities = [
        EntityData(id="P-0421", type="PERSON", name="Vikram Rao", aliases=["V. Rao", "Vikram"], source_ids=["FIR-001"]),
        EntityData(id="P-0312", type="PERSON", name="Rahul Mehta", aliases=["Rahul", "R. Mehta"], source_ids=["FIR-001"]),
        EntityData(id="P-0182", type="PERSON", name="Sana Iqbal", aliases=["Sana"], source_ids=["CDR-001"]),
        EntityData(id="O-1101", type="ORGANIZATION", name="Orion Traders", source_ids=["FIR-001", "INT-001"]),
        EntityData(id="N-4821", type="PHONE", name="Phone 4821", source_ids=["CDR-001"]),
        EntityData(id="N-9044", type="PHONE", name="Phone 9044", source_ids=["CDR-001"]),
        EntityData(id="N-7712", type="PHONE", name="Phone 7712", source_ids=["CDR-001"]),
        EntityData(id="L-3007", type="LOCATION", name="Sector 17", source_ids=["LOC-001"]),
        EntityData(id="L-4002", type="LOCATION", name="Dock 4", source_ids=["LOC-001"]),
        EntityData(id="A-4200", type="ACCOUNT", name="Account 4200", source_ids=["TXN-001"]),
        EntityData(id="A-0182", type="ACCOUNT", name="Account 0182", source_ids=["TXN-001"]),
        EntityData(id="V-2048", type="VEHICLE", name="VX-2048", source_ids=["VEH-001"]),
    ]

    relationships = [
        RelData(source="P-0421", target="O-1101", rel_type="MEMBER_OF", confidence=0.92,
                source_ids=["FIR-001"], first_seen="2026-07-01T08:00", last_seen="2026-07-01T08:00", count=1),
        RelData(source="P-0421", target="N-4821", rel_type="USES", confidence=0.94,
                source_ids=["CDR-001"], first_seen="2026-07-02T09:00", last_seen="2026-08-14T15:00", count=4,
                timestamps=["2026-07-02T09:00", "2026-08-10T11:00"]),
        RelData(source="N-4821", target="N-9044", rel_type="CALLED", confidence=0.85,
                source_ids=["CDR-001"], first_seen="2026-08-14T09:12", last_seen="2026-08-15T09:18", count=5,
                timestamps=["2026-08-14T09:12", "2026-08-14T09:18", "2026-08-14T09:31",
                            "2026-08-14T09:44", "2026-08-15T08:02"]),
        RelData(source="N-9044", target="P-0312", rel_type="USES", confidence=0.87,
                source_ids=["CDR-001"], first_seen="2026-08-14T09:00", last_seen="2026-08-14T09:00", count=1),
        RelData(source="N-4821", target="N-7712", rel_type="CALLED", confidence=0.82,
                source_ids=["CDR-001"], first_seen="2026-08-14T10:45", last_seen="2026-08-15T14:16", count=3,
                timestamps=["2026-08-14T10:45", "2026-08-15T14:16"]),
        RelData(source="N-7712", target="P-0182", rel_type="USES", confidence=0.84,
                source_ids=["CDR-001"], first_seen="2026-08-14T10:00", last_seen="2026-08-14T10:00", count=1),
        RelData(source="N-9044", target="L-4002", rel_type="USES", confidence=0.82,
                source_ids=["LOC-001"], first_seen="2026-08-14T09:25", last_seen="2026-08-14T09:25", count=1),
        RelData(source="N-4821", target="L-3007", rel_type="USES", confidence=0.86,
                source_ids=["LOC-001"], first_seen="2026-08-14T09:00", last_seen="2026-08-15T08:30", count=2,
                timestamps=["2026-08-14T09:00", "2026-08-15T08:30"]),
        RelData(source="N-9044", target="L-3007", rel_type="USES", confidence=0.7,
                source_ids=["LOC-002"], first_seen="2026-08-15T12:00", last_seen="2026-08-15T12:00", count=1,
                timestamps=["2026-08-15T12:00"]),
        RelData(source="A-4200", target="A-0182", rel_type="TRANSFERRED_TO", confidence=0.97,
                source_ids=["TXN-001", "TXN-002"], first_seen="2026-08-14T09:30", last_seen="2026-08-15T12:45",
                count=3, amount=2_400_000, strength=0.9,
                timestamps=["2026-08-14T09:30", "2026-08-15T09:00", "2026-08-15T12:45"]),
        RelData(source="A-0182", target="A-4200", rel_type="TRANSFERRED_TO", confidence=0.9,
                source_ids=["TXN-001"], first_seen="2026-08-14T10:05", last_seen="2026-08-14T10:05",
                count=1, amount=650_000),
        RelData(source="P-0421", target="A-4200", rel_type="OWNS", confidence=0.9,
                source_ids=["TXN-001"], first_seen="2026-08-14T09:00", last_seen="2026-08-14T09:00", count=1),
        RelData(source="P-0421", target="V-2048", rel_type="OWNS", confidence=0.95,
                source_ids=["VEH-001"], first_seen="2026-08-01T08:00", last_seen="2026-08-01T08:00", count=1),
        RelData(source="P-0312", target="V-2048", rel_type="HAS_ACCESS", confidence=0.5,
                source_ids=["SURV-001"], first_seen="2026-08-14T11:50", last_seen="2026-08-14T11:50", count=1,
                timestamps=["2026-08-14T11:50"]),
        RelData(source="P-0312", target="O-1101", rel_type="MEMBER_OF", confidence=0.72,
                source_ids=["INT-001"], first_seen="2026-08-10T09:00", last_seen="2026-08-10T09:00", count=1,
                timestamps=["2026-08-10T09:00"]),
        RelData(source="N-9044", target="N-7712", rel_type="CALLED", confidence=0.6,
                source_ids=["CDR-001"], first_seen="2026-08-14T16:05", last_seen="2026-08-15T10:00", count=2,
                timestamps=["2026-08-14T16:05", "2026-08-15T10:00"]),
    ]

    evidence = [
        _evidence("FIR-001", "FIR", "Smuggling under Orion Traders; Vikram Rao and Rahul Mehta named.",
                  ["P-0421", "P-0312", "O-1101"], 0.8),
        _evidence("CDR-001", "CDR", "High call volume between phones 4821 and 9044.",
                  ["N-4821", "N-9044"], 0.85),
        _evidence("CDR-002", "CDR", "Repeated late-night contact 4821→7712.",
                  ["N-4821", "N-7712"], 0.85),
        _evidence("TXN-001", "TRANSACTION", "Transfer 2.4M from 4200 to 0182.",
                  ["A-4200", "A-0182"], 0.85),
        _evidence("TXN-002", "TRANSACTION", "Second large transfer 4200→0182.",
                  ["A-4200", "A-0182"], 0.85),
        _evidence("LOC-001", "LOCATION", "Vehicle VX-2048 repeatedly observed at Sector 17.",
                  ["V-2048", "L-3007"], 0.65),
        _evidence("SURV-001", "SURVEILLANCE", "Handover observed; Rahul Mehta near warehouse.",
                  ["P-0312", "V-2048"], 0.6),
        _evidence("VEH-001", "VEHICLE", "VX-2048 registered to Vikram Rao.",
                  ["V-2048", "P-0421"], 0.7),
    ]

    return CaseData(case_number="DEMO-CASE", entities=entities, relationships=relationships, evidence=evidence)


def location_observations() -> dict[str, int]:
    return {"Sector 17": 4, "Dock 4": 3, "Kandivali West": 2, "Malad Industrial": 2, "BKC": 1}


def sample_anomalies() -> list[Anomaly]:
    return [
        Anomaly(kind="COMM_BURST", entity_id="N-4821", baseline=1.0, observed=5.0, deviation=400.0,
                score=91.0, timestamp="2026-08-14T09:00",
                evidence=["Phone 4821 initiated 5 calls within a 1-hour window"],
                explanation="Unusual communication burst (investigative signal, not a finding)."),
        Anomaly(kind="TX_AMOUNT", entity_id="A-4200->A-0182", baseline=650_000, observed=2_400_000,
                deviation=269.0, score=82.0, timestamp="2026-08-14T09:30",
                evidence=["Transfer 2,400,000 vs median 650,000"],
                explanation="High-value transfer flagged as unusual financial activity."),
    ]


def sample_potential_links() -> list[PotentialLink]:
    return [
        PotentialLink(source="P-0421", target="P-0312", score=73.0,
                      supporting_signals=["Shared organization (1)", "Shared location (1)",
                                          "Common intermediary", "Temporal overlap"],
                      confidence=0.73,
                      explanation="P-0421 ↔ P-0312 is a POTENTIAL relationship (not directly "
                                  "observed) supported by shared organization, location and an "
                                  "intermediary. Requires confirmation."),
    ]