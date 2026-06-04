from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.contact import Contact


class AppointmentStatus(str, enum.Enum):
    REQUESTED = "requested"      # el cliente la pidió (por agendar/confirmar)
    CONFIRMED = "confirmed"      # el negocio la confirmó
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AppointmentSource(str, enum.Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    VOICE = "voice"
    MANUAL = "manual"           # creada a mano por el dueño en el panel


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Datos de la cita
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    service_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Fecha/hora de la cita. Puede ser None si el cliente no precisó la hora exacta
    # (queda como solicitud para que el negocio coordine).
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Texto libre tal cual lo dijo el cliente ("el viernes a las 5", etc.).
    raw_when: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus, name="appointment_status_enum"),
        nullable=False,
        default=AppointmentStatus.REQUESTED,
    )
    source: Mapped[AppointmentSource] = mapped_column(
        SAEnum(AppointmentSource, name="appointment_source_enum"),
        nullable=False,
        default=AppointmentSource.WHATSAPP,
    )

    # Banderas de notificación/recordatorio (para no repetir).
    owner_notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped[Tenant] = relationship("Tenant", lazy="noload")
    contact: Mapped[Contact | None] = relationship("Contact", lazy="noload")

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, service={self.service_name}, when={self.scheduled_at})>"
