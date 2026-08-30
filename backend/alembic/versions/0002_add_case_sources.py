"""add case_sources table (Phase 2-3 source registry).

Revision ID: 0002_add_case_sources
Revises: 0001_baseline
Create Date: 2026-08-30
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0002_add_case_sources"
down_revision: str | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE case_sources (
            id BIGSERIAL PRIMARY KEY,
            case_id BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            source_id VARCHAR(64) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(32),
            source_type VARCHAR(32),
            status VARCHAR(24) NOT NULL DEFAULT 'UPLOADED',
            record_count INTEGER,
            processing_error VARCHAR(512),
            metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
            uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            processed_at TIMESTAMPTZ,
            UNIQUE (case_id, source_id)
        );
        CREATE INDEX idx_case_sources_case ON case_sources (case_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS case_sources;")