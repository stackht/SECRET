"""add investigative_leads table (Phase 12).

Revision ID: 0006_add_investigative_leads
Revises: 0005_nullable_generated_ids
Create Date: 2026-09-01
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0006_add_investigative_leads"
down_revision: str | None = "0005_nullable_generated_ids"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE investigative_leads (
            id BIGSERIAL PRIMARY KEY,
            case_id BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            kind VARCHAR(40) NOT NULL DEFAULT 'POTENTIAL_LINK',
            title VARCHAR(255) NOT NULL,
            description TEXT,
            priority FLOAT NOT NULL DEFAULT 0,
            info_gain FLOAT NOT NULL DEFAULT 0,
            status VARCHAR(24) NOT NULL DEFAULT 'NEW',
            entity_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
            evidence_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
            recommended_action TEXT,
            recommended_source VARCHAR(64),
            explanation TEXT,
            notes TEXT,
            created_by_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX idx_leads_case ON investigative_leads (case_id);
        CREATE INDEX idx_leads_status ON investigative_leads (status);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS investigative_leads;")