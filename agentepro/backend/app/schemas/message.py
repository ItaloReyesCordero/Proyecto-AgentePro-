from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.message import Message
from app.utils.helpers import enum_value


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    direction: str
    message_type: str
    content: str
    media_url: str | None
    transcription: str | None
    sender_type: str
    is_read: bool
    created_at: datetime
    tokens_used: int

    @classmethod
    def from_model(cls, m: Message) -> "MessageOut":
        return cls(
            id=m.id,
            conversation_id=m.conversation_id,
            direction=enum_value(m.direction),
            message_type=enum_value(m.message_type),
            content=m.content or "",
            media_url=m.media_url,
            transcription=m.transcription,
            sender_type=enum_value(m.sender_type),
            is_read=m.is_read,
            created_at=m.created_at,
            tokens_used=m.tokens_used,
        )


class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "text"
