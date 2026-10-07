"""Persist rationale for chef verification decisions.

Revision ID: 20260930_chef_review_rationale
Revises: 20260930_chef_email_verification
Create Date: 2026-09-30 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260930_chef_review_rationale"
down_revision = "20260930_chef_email_verification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chef_verifications", sa.Column("rationale", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("chef_verifications", "rationale")
