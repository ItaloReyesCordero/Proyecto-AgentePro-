"""inicial_plan — agrega el valor 'inicial' al enum plan_type_enum

Revision ID: 007_inicial_plan
Revises: 006_appointments
Create Date: 2026-06-03 00:00:00
"""

from __future__ import annotations

from alembic import op

revision = "007_inicial_plan"
down_revision = "006_appointments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # Solo Postgres tiene tipos ENUM nativos. En SQLite (tests) el enum es un
    # VARCHAR con CHECK que se regenera del modelo, así que no hay nada que migrar.
    if bind.dialect.name == "postgresql":
        # OJO: SQLAlchemy mapea PlanType por NOMBRE → las etiquetas reales del
        # enum están en MAYÚSCULA (BASIC, PROFESSIONAL, ENTERPRISE, TRIAL), así
        # que el nuevo valor también va en mayúscula.
        # PG12+ permite ADD VALUE dentro de transacción mientras el valor no se
        # use en la misma transacción (aquí solo lo agregamos).
        op.execute("ALTER TYPE plan_type_enum ADD VALUE IF NOT EXISTS 'INICIAL' BEFORE 'BASIC'")


def downgrade() -> None:
    # Postgres no soporta quitar valores de un ENUM de forma simple; se deja como
    # no-op (los planes 'inicial' tendrían que reasignarse antes manualmente).
    pass
