"""Add the shared COMP-008 Admin decision audit table."""

from alembic import op
import sqlalchemy as sa


revision = "20261004_add_admin_decisions"
down_revision = "20260930_chef_review_rationale"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_type", sa.String(length=64), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_admin_decisions_subject",
        "admin_decisions",
        ["subject_type", "subject_id"],
        unique=False,
    )
    op.create_index(
        "ix_admin_decisions_actor_created",
        "admin_decisions",
        ["actor_user_id", "created_at"],
        unique=False,
    )
    op.create_index("ix_admin_decisions_created_at", "admin_decisions", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_admin_decisions_created_at", table_name="admin_decisions")
    op.drop_index("ix_admin_decisions_actor_created", table_name="admin_decisions")
    op.drop_index("ix_admin_decisions_subject", table_name="admin_decisions")
    op.drop_table("admin_decisions")
