from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.contact import Contact
from app.utils.helpers import derive_lead_stage, enum_value


class ContactOut(BaseModel):
    id: uuid.UUID
    wa_id: str | None
    phone: str | None
    name: str | None
    email: str | None
    lead_score: int
    lead_stage: str
    source: str
    total_interactions: int
    last_interaction_at: datetime | None
    tags: list[str]
    notes: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, c: Contact) -> "ContactOut":
        status = enum_value(c.status)
        return cls(
            id=c.id,
            wa_id=c.wa_id,
            phone=c.phone_number,
            name=c.full_name,
            email=c.email,
            lead_score=c.qualification_score,
            lead_stage=derive_lead_stage(status, c.qualification_score),
            source=enum_value(c.primary_channel),
            total_interactions=c.total_messages,
            last_interaction_at=c.last_interaction_at,
            tags=c.tags or [],
            notes=c.notes,
            created_at=c.created_at,
        )


class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    tags: list[str] | None = None
    lead_stage: str | None = None
    notes: str | None = None
