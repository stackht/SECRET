"""Deterministic synthetic data generator (original Phase 2).

Produces interconnected, seeded records across source types. Supports the 9
required scenarios so a specific demo/anomaly can be reproduced reliably.
All data is fictional.
"""
from __future__ import annotations

import random
from collections import OrderedDict

from app.ingestion.records import (
    CDR,
    CRIMINAL_HISTORY,
    FIR,
    INTELLIGENCE,
    LOCATION,
    SURVEILLANCE,
    TRANSACTION,
    VEHICLE,
    SourceRecord,
)

Scenario = str

SCENARIO_NORMAL = "NORMAL_NETWORK"
SCENARIO_DENSE = "DENSE_NETWORK"
SCENARIO_BRIDGE = "BRIDGE_NODE"
SCENARIO_TX_ANOMALY = "TRANSACTION_ANOMALY"
SCENARIO_COMM_ANOMALY = "COMMUNICATION_ANOMALY"
SCENARIO_TEMPORAL = "TEMPORAL_ANOMALY"
SCENARIO_ALIAS = "ENTITY_ALIAS"
SCENARIO_NOISY = "NOISY_DATA"
SCENARIO_MISSING = "MISSING_DATA"

ALL_SCENARIOS = [
    SCENARIO_NORMAL,
    SCENARIO_DENSE,
    SCENARIO_BRIDGE,
    SCENARIO_TX_ANOMALY,
    SCENARIO_COMM_ANOMALY,
    SCENARIO_TEMPORAL,
    SCENARIO_ALIAS,
    SCENARIO_NOISY,
    SCENARIO_MISSING,
]

# Canonical entity ids used across records (deterministic, interconnected).
P_HUB = "P-0421"
P_B = "P-0182"
P_C = "P-7712"
P_D = "P-3310"
O_A = "O-1101"
O_B = "O-2033"
V_1 = "V-2048"
V_2 = "V-1191"
N_1 = "N-4821"
N_2 = "N-9044"
L_1 = "L-3007"
L_2 = "L-4002"
A_1 = "A-4200"
A_2 = "A-0182"


class SyntheticGenerator:
    """Deterministically produce synthetic source records for a scenario."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._counter = 0

    def _nid(self) -> str:
        self._counter += 1
        return f"SR-{self._counter:04d}"

    def _ts(self, day: int = 14, hour: int = 10, minute: int = 0) -> str:
        return f"2026-08-{day:02d}T{hour:02d}:{minute:02d}:00"

    def _record(self, source_type: str, ts: str, text: str, fields: dict | None = None) -> SourceRecord:
        return SourceRecord(
            record_id=self._nid(),
            source_type=source_type,
            timestamp=ts,
            text=text,
            fields=fields or {},
        )

    # --- core records shared across scenarios ---

    def _base_records(self, noisy: bool = False) -> list[SourceRecord]:
        recs: list[SourceRecord] = [
            self._record(
                FIR,
                self._ts(10, 9, 0),
                "FIR reported by witness. Individual Person A (alias Alpha) observed at Sector 17 "
                "with organized group Orion. Vehicle VX-2048 present.",
                {"person": P_HUB, "org": O_A, "location": L_1, "vehicle": V_1},
            ),
            self._record(
                CDR,
                self._ts(11, 14, 20),
                "Call from phone 4821 to phone 9044, duration 240 seconds. Located near Sector 17.",
                {"caller_phone": N_1, "receiver_phone": N_2, "duration": 240, "location": L_1},
            ),
            self._record(
                TRANSACTION,
                self._ts(12, 18, 5),
                "Transfer of 2400000 from account 4200 to account 0182.",
                {"sender": A_1, "receiver": A_2, "amount": 2400000},
            ),
            self._record(
                VEHICLE,
                self._ts(13, 7, 30),
                "Vehicle VX-2048 registered to Person A. Black sedan observed at Dock 4.",
                {"vehicle": V_1, "owner": P_HUB, "location": L_2},
            ),
            self._record(
                INTELLIGENCE,
                self._ts(14, 20, 0),
                "Intelligence report: Person B is a member of Organization Meridian.",
                {"person": P_B, "org": O_B, "relationship": "member_of"},
            ),
        ]
        if noisy:
            # Unrelated/noise records interspersed.
            recs.append(
                self._record(
                    SOCIAL,
                    self._ts(11, 12, 45),
                    "Unrelated social post about local news. No entity linkage.",
                    {"noise": True},
                )
            )
        return recs

    def generate(self, scenario: str = SCENARIO_NORMAL) -> list[SourceRecord]:
        """Return deterministic records for the given scenario."""
        if scenario == SCENARIO_NORMAL:
            return self._base_records()
        if scenario == SCENARIO_DENSE:
            return self._dense()
        if scenario == SCENARIO_BRIDGE:
            return self._bridge()
        if scenario == SCENARIO_TX_ANOMALY:
            return self._tx_anomaly()
        if scenario == SCENARIO_COMM_ANOMALY:
            return self._comm_anomaly()
        if scenario == SCENARIO_TEMPORAL:
            return self._temporal()
        if scenario == SCENARIO_ALIAS:
            return self._alias()
        if scenario == SCENARIO_NOISY:
            return self._base_records(noisy=True)
        if scenario == SCENARIO_MISSING:
            return self._missing()
        return self._base_records()

    def _dense(self) -> list[SourceRecord]:
        recs = self._base_records()
        # Many connections out of the hub.
        for i in range(4):
            recs.append(
                self._record(
                    CDR,
                    self._ts(14, 9 + i, 0),
                    f"Call from {N_1} to phone {9000 + i}.",
                    {"caller_phone": N_1, "receiver_phone": f"N-{9000 + i}"},
                )
            )
        return recs

    def _bridge(self) -> list[SourceRecord]:
        # The hub connects two otherwise separate communities via P_C.
        recs = self._base_records()
        recs.append(
            self._record(
                INTELLIGENCE,
                self._ts(12, 16, 0),
                "Person C bridges Orion and Meridian; transit between both networks.",
                {"person": P_C, "relationship": "bridge"},
            )
        )
        return recs

    def _tx_anomaly(self) -> list[SourceRecord]:
        recs = self._base_records()
        # A burst of large transfers to a previously-unknown account.
        for i in range(6):
            recs.append(
                self._record(
                    TRANSACTION,
                    self._ts(13, 8 + i, 0),
                    f"Suspicious transfer {100000 + i * 50000} to new account.",
                    {"sender": A_1, "receiver": f"A-NEW{i}", "amount": 100000 + i * 50000},
                )
            )
        return recs

    def _comm_anomaly(self) -> list[SourceRecord]:
        recs = self._base_records()
        # A tight burst of short rapid calls (within 2 minutes) — a realistic
        # communication burst signal.
        for i in range(5):
            recs.append(
                self._record(
                    CDR,
                    self._ts(13, 0, i * 2),
                    f"Short rapid call {N_1}->{N_2} at night.",
                    {"caller_phone": N_1, "receiver_phone": N_2, "duration": 2},
                )
            )
        return recs

    def _temporal(self) -> list[SourceRecord]:
        # Several events at nearly the same timestamp across locations.
        recs = self._base_records()
        for i in range(3):
            recs.append(
                self._record(
                    SURVEILLANCE,
                    self._ts(14, 3, i),
                    "Motion at location during off-hours window.",
                    {"person": P_HUB, "location": L_1},
                )
            )
        return recs

    def _alias(self) -> list[SourceRecord]:
        recs = self._base_records()
        recs.append(
            self._record(
                CRIMINAL_HISTORY,
                self._ts(9, 11, 0),
                "Record shows 'Alpha' also known as 'A. Khan' and 'Person A'.",
                {"aliases": ["Alpha", "A. Khan", "Person A"], "person": P_HUB},
            )
        )
        return recs

    def _missing(self) -> list[SourceRecord]:
        recs = self._base_records()
        # A record with missing phone/location fields (incomplete data).
        recs.append(
            self._record(
                CDR,
                self._ts(14, 22, 0),
                "Call log entry missing caller identity.",
                {"caller_phone": None, "receiver_phone": N_2, "duration": None},
            )
        )
        return recs


def generate_synthetic(scenario: str = SCENARIO_NORMAL, seed: int = 42) -> list[SourceRecord]:
    return SyntheticGenerator(seed).generate(scenario)


def all_scenario_brief() -> dict[str, int]:
    return OrderedDict((s, len(generate_synthetic(s))) for s in ALL_SCENARIOS)
