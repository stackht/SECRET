"""Entity identifier helpers.

SECRET uses stable, human-readable typed identifiers aligned with the frontend
types (see src/types.ts) and the criminal_profiles.secret_id column.
"""
from typing import Literal

EntityTypePrefix = Literal["P", "O", "V", "N", "L", "A", "E"]

# Maps domain entity type to its id prefix.
PREFIX_BY_TYPE: dict[str, EntityTypePrefix] = {
    "PERSON": "P",          # Person
    "ORGANIZATION": "O",    # Organization
    "PHONE": "N",           # Phone (N to avoid clashing with P)
    "VEHICLE": "V",         # Vehicle
    "LOCATION": "L",        # Location
    "ACCOUNT": "A",         # Account
    "EVENT": "E",           # Event
}

TYPE_BY_PREFIX: dict[EntityTypePrefix, str] = {v: k for k, v in PREFIX_BY_TYPE.items()}


def build_secret_id(entity_type: str, sequence: int, width: int = 4) -> str:
    """Build a stable typed id, e.g. ('PERSON', 421) -> 'P-0421'."""
    prefix = PREFIX_BY_TYPE.get(entity_type.upper(), "E")
    return f"{prefix}-{sequence:0{width}d}"


def parse_secret_id(secret_id: str) -> tuple[EntityTypePrefix, int]:
    """Parse 'P-0421' into ('P', 421)."""
    prefix, _, num = secret_id.partition("-")
    return prefix.upper(), int(num)  # type: ignore[return-value]
