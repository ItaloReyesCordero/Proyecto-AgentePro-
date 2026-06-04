from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.appointment import Appointment
from app.utils.helpers import enum_value


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contact_id: uuid.UUID | None
    customer_name: str | None
    customer_phone: str | None
    service_name: str | None
    scheduled_at: datetime | None
    raw_when: str | None
    notes: str | None
    status: str
    source: str
    created_at: datetime

    @classmethod
    def from_model(cls, a: Appointment) -> "AppointmentOut":
        return cls(
            id=a.id,
            contact_id=a.contact_id,
            customer_name=a.customer_name,
            customer_phone=a.customer_phone,
            service_name=a.service_name,
            scheduled_at=a.scheduled_at,
            raw_when=a.raw_when,
            notes=a.notes,
            status=enum_value(a.status),
            source=enum_value(a.source),
            created_at=a.created_at,
        )


class AppointmentCreate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    service_name: str | None = None
    scheduled_at: datetime | None = None
    raw_when: str | None = None
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    service_name: str | None = None
    scheduled_at: datetime | None = None
    notes: str | None = None
    status: str | None = None
