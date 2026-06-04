"""notion_crm — credenciales de Notion como CRM por tenant

Revision ID: 005_notion_crm
Revises: 004_manual_billing
Create Date: 2026-06-03 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005_notion_crm"
down_revision = "004_manual_billing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("notion_api_key", sa.Text(), nullable=True))
    op.add_column("tenants", sa.Column("notion_database_id", sa.String(length=100), nullable=True))
    op.add_column(
        "tenants",
        sa.Column("notion_last_synced_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tenants", "notion_last_synced_at")
    op.drop_column("tenants", "notion_database_id")
    op.drop_column("tenants", "notion_api_key")
