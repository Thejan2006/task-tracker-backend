"""Restore the legacy migration identifier used by existing databases.

This revision is intentionally empty. Some existing databases recorded this
revision before the migration file was removed from the repository.
"""
from alembic import op


revision = "d4fe09619266"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
