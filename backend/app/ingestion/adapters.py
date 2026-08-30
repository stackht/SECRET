"""Ingestion source adapters (original Phase 3).

Transform raw synthetic source payloads into canonical `SourceRecord`s, and
provide a registry so the "run simulation" flow can ingest multiple source
types uniformly. This is the seam where real adapters (real FIR/CDR, etc.)
would plug in later.
"""
from __future__ import annotations

import abc

from app.ingestion.records import SourceRecord


class SourceAdapter(abc.ABC):
    """Base class for a source adapter."""

    source_type: str = ""

    @abc.abstractmethod
    def ingest(self, raw: dict) -> SourceRecord:
        """Convert a raw source payload into a canonical SourceRecord."""


class FIRAdapter(SourceAdapter):
    source_type = "FIR"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class CDRAdapter(SourceAdapter):
    source_type = "CDR"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class TransactionAdapter(SourceAdapter):
    source_type = "TRANSACTION"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class SurveillanceAdapter(SourceAdapter):
    source_type = "SURVEILLANCE"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class VehicleAdapter(SourceAdapter):
    source_type = "VEHICLE"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class IntelligenceAdapter(SourceAdapter):
    source_type = "INTELLIGENCE"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class SocialAdapter(SourceAdapter):
    source_type = "SOCIAL"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class CriminalHistoryAdapter(SourceAdapter):
    source_type = "CRIMINAL_HISTORY"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class LocationAdapter(SourceAdapter):
    source_type = "LOCATION"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


class OtherAdapter(SourceAdapter):
    source_type = "OTHER"

    def ingest(self, raw: dict) -> SourceRecord:
        return SourceRecord(
            record_id=str(raw["id"]),
            source_type=self.source_type,
            timestamp=raw.get("timestamp", ""),
            text=raw.get("text", ""),
            fields=raw,
        )


# Adapter registry keyed by source type.
ADAPTERS: dict[str, SourceAdapter] = {
    a.source_type: a()
    for a in (FIRAdapter, CDRAdapter, TransactionAdapter, SurveillanceAdapter,
              VehicleAdapter, IntelligenceAdapter, SocialAdapter,
              CriminalHistoryAdapter, LocationAdapter, OtherAdapter)
}


def normalize_record(source_type: str, raw: dict) -> SourceRecord:
    """Normalize a raw payload for a source into a SourceRecord."""
    adapter = ADAPTERS.get(source_type) or ADAPTERS["OTHER"]
    return adapter.ingest(raw)
