"""Backfill task timestamps and enforce their model constraints.

Revision ID: 20260914_backfill_task_timestamps
"""
from alembic import op
import sqlalchemy as sa


revision = "20260914_task_timestamps"
down_revision = "20260914_align_users_schema"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tasks" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "created_at" in columns:
        op.execute(
            "UPDATE tasks SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
        )
        op.alter_column(
            "tasks",
            "created_at",
            type_=sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            postgresql_using="created_at::TIMESTAMPTZ",
        )
    if "updated_at" in columns:
        op.execute(
            "UPDATE tasks SET updated_at = COALESCE(created_at, CURRENT_TIMESTAMP) "
            "WHERE updated_at IS NULL"
        )
        op.alter_column(
            "tasks",
            "updated_at",
            type_=sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            postgresql_using="updated_at::TIMESTAMPTZ",
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tasks" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("tasks")}
    for name in ("updated_at", "created_at"):
        if name in columns:
            op.alter_column(
                "tasks",
                name,
                nullable=True,
                server_default=None,
            )
