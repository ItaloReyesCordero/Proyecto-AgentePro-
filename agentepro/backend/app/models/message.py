from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.conversation import Conversation


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(str, enum.Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    TEMPLATE = "template"
    SYSTEM = "system"


class SenderType(str, enum.Enum):
    CONTACT = "contact"
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Anti-duplicate: unique WhatsApp message ID
    wa_message_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )

    # Direction & Type
    direction: Mapped[MessageDirection] = mapped_column(
        SAEnum(MessageDirection, name="message_direction_enum"),
        nullable=False,
    )
    message_type: Mapped[MessageType] = mapped_column(
        SAEnum(MessageType, name="message_type_enum"),
        nullable=False,
        default=MessageType.TEXT,
    )
    sender_type: Mapped[SenderType] = mapped_column(
        SAEnum(SenderType, name="sender_type_enum"),
        nullable=False,
        default=SenderType.CONTACT,
    )

    # Content
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcription: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI Usage
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, direction={self.direction}, type={self.message_type})>"
