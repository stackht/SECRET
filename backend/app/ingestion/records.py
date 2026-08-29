"""Canonical record models (ingestion layer).

`SourceRecord` is the normalized, storage-agnostic unit produced by ingestion
adapters and consumed by extraction / resolution. All data is synthetic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Source types (adapter registry keys).
FIR = "FIR"
CDR = "CDR"
TRANSACTION = "TRANSACTION"
SURVEILLANCE = "SURVEILLANCE"
SOCIAL = "SOCIAL"
CRIMINAL_HISTORY = "CRIMINAL_HISTORY"
INTELLIGENCE = "INTELLIGENCE"
VEHICLE = "VEHICLE"
LOCATION = "LOCATION"


@dataclass
class SourceRecord:
    """A single canonical raw record from a source."""

    record_id: str
    source_type: str                       # one of the source constants
    timestamp: str                         # ISO 8601
    text: str                              # human-readable content (for NLP extraction)
    fields: dict[str, Any] = field(default_factory=dict)
