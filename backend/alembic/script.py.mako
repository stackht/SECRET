"""Alembic migration template."""
# type: ignore

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = None
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply the migration."""


def downgrade() -> None:
    """Revert the migration."""
