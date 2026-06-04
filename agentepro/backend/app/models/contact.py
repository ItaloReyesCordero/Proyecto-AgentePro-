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
    from app.models.conversation import Conversation


class ContactStatus(str, enum.Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class ContactChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    VOICE = "voice"
    WEB = "web"


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Identity
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # WhatsApp / Instagram identifiers
    wa_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    instagram_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status & Classification
    status: Mapped[ContactStatus] = mapped_column(
        SAEnum(ContactStatus, name="contact_status_enum"),
        nullable=False,
        default=ContactStatus.LEAD,
    )
    primary_channel: Mapped[ContactChannel] = mapped_column(
        SAEnum(ContactChannel, name="contact_channel_enum"),
        nullable=False,
        default=ContactChannel.WHATSAPP,
    )

    # CRM Data
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    custom_fields: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lead Qualification
    is_qualified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    qualification_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qualification_answers: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )

    # HubSpot
    hubspot_contact_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Statistics
    total_conversations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_interaction_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Consent
    opted_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    opted_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="contacts")
    conversations: Mapped[list[Conversation]] = relationship(
        "Conversation", back_populates="contact", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, phone={self.phone_number}, name={self.full_name})>"
