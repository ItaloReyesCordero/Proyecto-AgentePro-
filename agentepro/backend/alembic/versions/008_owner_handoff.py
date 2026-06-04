"""owner_handoff — números del dueño (amigos/familia) + mensaje de "pasar con el dueño"

Revision ID: 008_owner_handoff
Revises: 007_inicial_plan
Create Date: 2026-06-03 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "008_owner_handoff"
down_revision = "007_inicial_plan"
branch_labels = None
depends_on = None

_DEFAULT_MSG = (
    "¡Hola! 😊 Para este tema te comunico directamente con el dueño. "
    "En un momento te contactará personalmente."
)


def upgrade() -> None:
    op.add_column(
        "agent_configs",
        sa.Column(
            "owner_contacts",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )
    op.add_column(
        "agent_configs",
        sa.Column(
            "owner_handoff_message",
            sa.Text(),
            nullable=False,
            server_default=_DEFAULT_MSG,
        ),
    )


def downgrade() -> None:
    op.drop_column("agent_configs", "owner_handoff_message")
    op.drop_column("agent_configs", "owner_contacts")
