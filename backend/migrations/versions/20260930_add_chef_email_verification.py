"""Add chef email verification state and certificate reference.

Revision ID: 20260930_chef_email_verification
Revises: 20260930_auth_sessions
Create Date: 2026-09-30 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260930_chef_email_verification"
down_revision = "20260930_auth_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_email_verification_tokens_user_id"),
        sa.UniqueConstraint("token_hash", name="uq_email_verification_tokens_token_hash"),
    )
    op.alter_column(
        "chef_verifications",
        "certificate_url",
        new_column_name="certificate_ref",
        existing_type=sa.String(length=512),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "chef_verifications",
        "certificate_ref",
        new_column_name="certificate_url",
        existing_type=sa.String(length=512),
        nullable=True,
    )
    op.drop_table("email_verification_tokens")
    op.drop_column("users", "email_verified")