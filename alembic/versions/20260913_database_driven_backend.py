"""Add task workflow, profile, and activity fields.

Revision ID: 20260913_database_driven_backend
"""
from alembic import op
import sqlalchemy as sa

revision = "20260913_database_driven_backend"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    if "users" in tables:
        columns = {c["name"] for c in inspector.get_columns("users")}
        for name, column in (
            ("name", sa.Column("name", sa.String(), nullable=True)),
            ("bio", sa.Column("bio", sa.Text(), nullable=True)),
            ("avatar_url", sa.Column("avatar_url", sa.String(), nullable=True)),
            ("is_active", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true())),
            ("created_at", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)),
        ):
            if name not in columns:
                op.add_column("users", column)
    if "tasks" in tables:
        columns = {c["name"] for c in inspector.get_columns("tasks")}
        for name, column in (
            ("priority", sa.Column("priority", sa.String(), nullable=True)),
            ("status", sa.Column("status", sa.String(), nullable=False, server_default="todo")),
            ("position", sa.Column("position", sa.Integer(), nullable=False, server_default="0")),
            ("created_at", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)),
            ("updated_at", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)),
        ):
            if name not in columns:
                op.add_column("tasks", column)
        op.execute("UPDATE tasks SET status = CASE WHEN is_completed = TRUE THEN 'done' ELSE 'todo' END WHERE status IS NULL")
        op.execute("UPDATE tasks SET position = 0 WHERE position IS NULL")
    if "activities" not in tables:
        op.create_table(
            "activities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("type", sa.String(), nullable=False),
            sa.Column("message", sa.String(), nullable=False),
            sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "tasks" in tables:
        # Rebuild legacy positions deterministically per owner and status.
        rows = bind.execute(sa.text("SELECT id, owner_id, status FROM tasks ORDER BY owner_id, status, id")).fetchall()
        counters = {}
        for task_id, owner_id, status in rows:
            key = (owner_id, status)
            position = counters.get(key, 0)
            bind.execute(sa.text("UPDATE tasks SET position = :position WHERE id = :id"),
                         {"position": position, "id": task_id})
            counters[key] = position + 1

def downgrade():
    op.drop_table("activities")
    for table, names in (("tasks", ("updated_at", "created_at", "position", "status", "priority")),
                         ("users", ("created_at", "is_active", "avatar_url", "bio", "name"))):
        for name in names:
            op.drop_column(table, name)
