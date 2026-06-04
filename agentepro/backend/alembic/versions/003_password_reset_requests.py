"""password_reset_requests

Revision ID: 003_password_reset
Revises: 002_calls_instagram_hubspot
Create Date: 2026-06-01 00:02:00
"""

from __future__ import annotations

from alembic import op

from app.database import Base
import app.models  # noqa: F401

revision = "003_password_reset"
down_revision = "002_calls_instagram_hubspot"
branch_labels = None
depends_on = None

_NEW_TABLES = ["password_reset_requests"]


def upgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in _NEW_TABLES if name in Base.metadata.tables]
    Base.metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in reversed(_NEW_TABLES) if name in Base.metadata.tables]
    Base.metadata.drop_all(bind=bind, tables=tables, checkfirst=True)
