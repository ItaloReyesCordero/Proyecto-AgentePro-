"""calls, call_summaries, instagram_posts, hubspot_sync_logs

Revision ID: 002_calls_instagram_hubspot
Revises: 001_initial
Create Date: 2026-01-01 00:01:00
"""

from __future__ import annotations

from alembic import op

from app.database import Base
import app.models  # noqa: F401

revision = "002_calls_instagram_hubspot"
down_revision = "001_initial"
branch_labels = None
depends_on = None

_NEW_TABLES = [
    "calls",
    "call_summaries",
    "instagram_posts",
    "hubspot_sync_logs",
]


def upgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in _NEW_TABLES if name in Base.metadata.tables]
    Base.metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in reversed(_NEW_TABLES) if name in Base.metadata.tables]
    Base.metadata.drop_all(bind=bind, tables=tables, checkfirst=True)
