"""convert enum columns to VARCHAR (live-PG ORM compatibility).

Revision ID: 0004_drop_enums
Revises: 0003_add_entities
Create Date: 2026-08-30

The Phase 1 schema used native PG enums; SQLAlchemy ORM models declare these
columns as VARCHAR, so parameterized inserts raise DatatypeMismatchError on
PostgreSQL (SQLite tests never hit this). Converting the columns to plain
VARCHAR aligns the database with the ORM and restores live inserts.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0004_drop_enums"
down_revision: str | None = "0003_add_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ALTERS = [
    ("users", "role", 16, "user_role"),
    ("users", "status", 16, "user_status"),
    ("criminal_profiles", "profile_type", 16, "entity_type"),
    ("criminal_profiles", "risk_level", 16, "risk_level"),
    ("cases", "status", 16, "case_status"),
    ("cases", "priority", 16, "case_priority"),
    ("evidence", "evidence_type", 16, "evidence_type"),
    ("alerts", "severity", 16, "alert_severity"),
    ("alerts", "status", 24, "alert_status"),
    ("firs", "status", 24, "fir_status"),
]


def upgrade() -> None:
    for table, column, size, enum_type in _ALTERS:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN {column} TYPE VARCHAR({size}) "
            f"USING {column}::text"
        )
        op.execute(f"ALTER TABLE {table} ALTER COLUMN {column} DROP DEFAULT")
    for enum_type in sorted({e for _, _, _, e in _ALTERS}):
        op.execute(f"DROP TYPE IF EXISTS {enum_type}")


def downgrade() -> None:
    raise NotImplementedError("Recreating enum columns is not supported; restore from backup instead.")