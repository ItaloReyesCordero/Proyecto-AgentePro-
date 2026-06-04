"""initial schema — tenants, users, contacts, conversations, messages, configs, automations

Revision ID: 001_initial
Revises:
Create Date: 2026-01-01 00:00:00
"""

from __future__ import annotations

from alembic import op

from app.database import Base
import app.models  # noqa: F401  (registra los modelos)

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None

# Tablas creadas en la migración base.
_CORE_TABLES = [
    "tenants",
    "users",
    "contacts",
    "conversations",
    "messages",
    "agent_configs",
    "voice_configs",
    "subscriptions",
    "automations",
    "automation_runs",
    "webhook_logs",
]


def upgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in _CORE_TABLES if name in Base.metadata.tables]
    Base.metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in reversed(_CORE_TABLES) if name in Base.metadata.tables]
    Base.metadata.drop_all(bind=bind, tables=tables, checkfirst=True)
