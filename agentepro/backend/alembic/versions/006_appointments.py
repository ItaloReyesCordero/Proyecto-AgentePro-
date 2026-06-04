"""appointments — citas detectadas por el agente + recordatorios

Revision ID: 006_appointments
Revises: 005_notion_crm
Create Date: 2026-06-03 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "006_appointments"
down_revision = "005_notion_crm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IMPORTANTE: SQLAlchemy mapea los Enum por NOMBRE de miembro (mayúsculas),
    # igual que el resto de enums del sistema (plan_type_enum = {BASIC,...}).
    # Por eso las etiquetas van en MAYÚSCULA, no por el .value.
    # create_type=False: los creamos explícitamente abajo, así create_table NO
    # intenta volver a crear el tipo (daría "type already exists").
    status_enum = postgresql.ENUM(
        "REQUESTED", "CONFIRMED", "CANCELLED", "COMPLETED",
        name="appointment_status_enum", create_type=False,
    )
    source_enum = postgresql.ENUM(
        "WHATSAPP", "INSTAGRAM", "VOICE", "MANUAL",
        name="appointment_source_enum", create_type=False,
    )
    status_enum.create(op.get_bind(), checkfirst=True)
    source_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_phone", sa.String(length=30), nullable=True),
        sa.Column("service_name", sa.String(length=255), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_when", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", status_enum, nullable=False, server_default="REQUESTED"),
        sa.Column("source", source_enum, nullable=False, server_default="WHATSAPP"),
        sa.Column("owner_notified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("appointments")
    postgresql.ENUM(name="appointment_status_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="appointment_source_enum").drop(op.get_bind(), checkfirst=True)
