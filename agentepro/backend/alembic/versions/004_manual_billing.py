"""manual_billing — campos de cobro manual en tenants

Revision ID: 004_manual_billing
Revises: 003_password_reset
Create Date: 2026-06-02 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "004_manual_billing"
down_revision = "003_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("next_payment_due", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tenants", sa.Column("last_payment_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tenants", sa.Column("monthly_amount_pen", sa.Integer(), nullable=True))
    op.add_column(
        "tenants",
        sa.Column(
            "billing_suspended",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("tenants", "billing_suspended")
    op.drop_column("tenants", "monthly_amount_pen")
    op.drop_column("tenants", "last_payment_at")
    op.drop_column("tenants", "next_payment_due")
