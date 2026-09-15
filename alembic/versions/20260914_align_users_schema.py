"""Align the users table with the User model.

Revision ID: 20260914_align_users_schema
"""
from alembic import op
import sqlalchemy as sa


revision = "20260914_align_users_schema"
down_revision = ("20260913_database_driven_backend", "d4fe09619266")
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("hashed_password", sa.String(), nullable=False),
            sa.Column("role", sa.String(), nullable=False, server_default="user"),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("bio", sa.Text(), nullable=True),
            sa.Column("avatar_url", sa.String(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("otp", sa.String(), nullable=True),
            sa.Column("otp_code", sa.String(), nullable=True),
            sa.UniqueConstraint("username", name="uq_users_username"),
            sa.UniqueConstraint("email", name="uq_users_email"),
        )
        return

    columns = {column["name"] for column in inspector.get_columns("users")}

    # The existing application must provide values for these fields. Adding
    # them as nullable first lets PostgreSQL report any legacy data problem
    # before the NOT NULL constraint is applied.
    required_columns = (
        ("username", sa.String()),
        ("email", sa.String()),
        ("hashed_password", sa.String()),
        ("role", sa.String()),
    )
    for name, column_type in required_columns:
        if name not in columns:
            op.add_column("users", sa.Column(name, column_type, nullable=True))

    optional_columns = (
        ("name", sa.String()),
        ("bio", sa.Text()),
        ("avatar_url", sa.String()),
        ("is_active", sa.Boolean()),
        ("created_at", sa.DateTime(timezone=True)),
        ("is_verified", sa.Boolean()),
        ("otp", sa.String()),
        ("otp_code", sa.String()),
    )
    for name, column_type in optional_columns:
        if name not in columns:
            op.add_column("users", sa.Column(name, column_type, nullable=True))

    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
    op.execute("UPDATE users SET is_active = TRUE WHERE is_active IS NULL")
    op.execute("UPDATE users SET is_verified = FALSE WHERE is_verified IS NULL")
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    # These checks produce a useful migration error instead of silently
    # inventing credentials or identifiers for existing users.
    for name in ("username", "email", "hashed_password"):
        op.execute(
            sa.text(
                f"DO $migration$ BEGIN "
                f"IF EXISTS (SELECT 1 FROM users WHERE {name} IS NULL) THEN "
                f"RAISE EXCEPTION 'users.{name} contains NULL values; populate them before migration'; "
                "END IF; END $migration$;"
            )
        )

    if "id" not in columns:
        raise RuntimeError(
            "users.id is missing; restore the primary-key column before running this migration"
        )

    for name in ("username", "email", "hashed_password", "role", "name", "avatar_url", "otp", "otp_code"):
        op.alter_column(
            "users",
            name,
            type_=sa.String(),
            postgresql_using=f"{name}::VARCHAR",
        )
    op.alter_column("users", "bio", type_=sa.Text(), postgresql_using="bio::TEXT")
    for name in ("is_active", "is_verified"):
        op.alter_column(
            "users",
            name,
            type_=sa.Boolean(),
            postgresql_using=f"{name}::BOOLEAN",
        )
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at::TIMESTAMPTZ",
    )

    for name in ("username", "email", "hashed_password", "role"):
        op.alter_column("users", name, nullable=False)
    op.alter_column("users", "is_active", nullable=False, server_default=sa.true())
    op.alter_column("users", "is_verified", nullable=False, server_default=sa.false())
    op.alter_column(
        "users",
        "created_at",
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    existing_unique_columns = {
        tuple(sorted(constraint["column_names"]))
        for constraint in inspector.get_unique_constraints("users")
    }
    if ("username",) not in existing_unique_columns:
        op.create_unique_constraint("uq_users_username", "users", ["username"])
    if ("email",) not in existing_unique_columns:
        op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" not in inspector.get_table_names():
        return

    for name in ("uq_users_username", "uq_users_email"):
        if name in {
            constraint["name"]
            for constraint in inspector.get_unique_constraints("users")
        }:
            op.drop_constraint(name, "users", type_="unique")

    columns = {column["name"] for column in inspector.get_columns("users")}
    for name in ("otp_code", "otp", "is_verified"):
        if name in columns:
            op.drop_column("users", name)
