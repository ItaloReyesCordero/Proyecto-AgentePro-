from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.contact import Contact
    from app.models.message import Message


class ConversationStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    ESCALATED = "escalated"
    CLOSED = "closed"


class ConversationChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    VOICE = "voice"
    WEB = "web"


class ConversationAssigneeType(str, enum.Enum):
    AI = "ai"
    HUMAN = "human"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Channel & Status
    channel: Mapped[ConversationChannel] = mapped_column(
        SAEnum(ConversationChannel, name="conversation_channel_enum"),
        nullable=False,
        default=ConversationChannel.WHATSAPP,
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SAEnum(ConversationStatus, name="conversation_status_enum"),
        nullable=False,
        default=ConversationStatus.OPEN,
        index=True,
    )
    assignee_type: Mapped[ConversationAssigneeType] = mapped_column(
        SAEnum(ConversationAssigneeType, name="conversation_assignee_type_enum"),
        nullable=False,
        default=ConversationAssigneeType.AI,
    )
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # WhatsApp specific
    wa_conversation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Content
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI Context
    ai_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    last_ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Statistics
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unread_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Flags
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_spam: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps
    first_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="conversations")
    contact: Mapped[Contact] = relationship("Contact", back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(
        "Message", back_populates="conversation", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, status={self.status}, channel={self.channel})>"
