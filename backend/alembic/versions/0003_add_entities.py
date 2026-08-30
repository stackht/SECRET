"""add entities + entity_relationships tables (Phase 2 persistence).

Revision ID: 0003_add_entities
Revises: 0002_add_case_sources
Create Date: 2026-08-30
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0003_add_entities"
down_revision: str | None = "0002_add_case_sources"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE entities (
            id BIGSERIAL PRIMARY KEY,
            case_id BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            entity_id VARCHAR(128) NOT NULL,
            entity_type VARCHAR(32) NOT NULL,
            name VARCHAR(255) NOT NULL DEFAULT 'Unknown',
            confidence FLOAT NOT NULL DEFAULT 0,
            attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
            source_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (case_id, entity_id, entity_type)
        );
        CREATE INDEX idx_entities_case ON entities (case_id);
        CREATE INDEX idx_entities_type ON entities (entity_type);

        CREATE TABLE entity_relationships (
            id BIGSERIAL PRIMARY KEY,
            case_id BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            rel_type VARCHAR(40) NOT NULL,
            source_id VARCHAR(128) NOT NULL,
            target_id VARCHAR(128) NOT NULL,
            confidence FLOAT NOT NULL DEFAULT 0,
            source_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
            attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (case_id, rel_type, source_id, target_id)
        );
        CREATE INDEX idx_entity_relationships_case ON entity_relationships (case_id);
        CREATE INDEX idx_entity_relationships_source ON entity_relationships (source_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS entity_relationships; DROP TABLE IF EXISTS entities;")