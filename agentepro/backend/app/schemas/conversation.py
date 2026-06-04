from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.contact import Contact
from app.models.conversation import Conversation
from app.schemas.contact import ContactOut
from app.schemas.message import MessageOut
from app.utils.helpers import derive_lead_stage, enum_value

# Estados internos -> estados que entiende el frontend.
_STATUS_MAP = {
    "open": "open",
    "in_progress": "open",
    "waiting": "waiting",
    "escalated": "human_takeover",
    "closed": "closed",
}


class ConversationOut(BaseModel):
    id: uuid.UUID
    contact: ContactOut | None
    channel: str
    status: str
    assigned_to_human: bool
    lead_score: int
    lead_stage: str
    last_message_at: datetime | None
    tags: list[str]
    unread_count: int = 0
    last_message: MessageOut | None = None

    @classmethod
    def from_model(
        cls,
        conv: Conversation,
        contact: Contact | None = None,
        last_message: MessageOut | None = None,
    ) -> "ConversationOut":
        channel = enum_value(conv.channel)
        # El frontend usa 'instagram_dm'; el modelo usa 'instagram'.
        if channel == "instagram":
            channel = "instagram_dm"
        score = contact.qualification_score if contact else 0
        status_val = enum_value(conv.status)
        assigned_human = enum_value(conv.assignee_type) == "human" or status_val == "escalated"
        return cls(
            id=conv.id,
            contact=ContactOut.from_model(contact) if contact else None,
            channel=channel,
            status=_STATUS_MAP.get(status_val, "open"),
            assigned_to_human=assigned_human,
            lead_score=score,
            lead_stage=derive_lead_stage(enum_value(contact.status) if contact else None, score),
            last_message_at=conv.last_message_at,
            tags=conv.tags or [],
            unread_count=conv.unread_count,
            last_message=last_message,
        )


class ConversationUpdate(BaseModel):
    tags: list[str] | None = None
    lead_stage: str | None = None
    status: str | None = None
