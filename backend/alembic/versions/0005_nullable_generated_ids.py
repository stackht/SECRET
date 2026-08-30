"""align generated-identifier columns with the ORM (nullable).

Revision ID: 0005_nullable_generated_ids
Revises: 0004_drop_enums
Create Date: 2026-08-30

`case_number` and `secret_id` are derived from the DB id by the service layer
after insert (CASE-2026-0001 / P-0421). The ORM declares them nullable;
the Phase 1 DDL made them NOT NULL, which rejects the initial INSERT on live
PostgreSQL (SQLite tests never noticed). Dropping NOT NULL keeps the unique
constraint while allowing insert-then-derive.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0005_nullable_generated_ids"
down_revision: str | None = "0004_drop_enums"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE cases ALTER COLUMN case_number DROP NOT NULL")
    op.execute("ALTER TABLE criminal_profiles ALTER COLUMN secret_id DROP NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE cases ALTER COLUMN case_number SET NOT NULL")
    op.execute("ALTER TABLE criminal_profiles ALTER COLUMN secret_id SET NOT NULL")