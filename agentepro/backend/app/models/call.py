from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.contact import Contact
    from app.models.call_summary import CallSummary


class CallStatus(str, enum.Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    CANCELLED = "cancelled"


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Call(Base):
    __tablename__ = "calls"

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

    # External IDs
    retell_call_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    twilio_call_sid: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )

    # Call Details
    direction: Mapped[CallDirection] = mapped_column(
        SAEnum(CallDirection, name="call_direction_enum"),
        nullable=False,
        default=CallDirection.INBOUND,
    )
    status: Mapped[CallStatus] = mapped_column(
        SAEnum(CallStatus, name="call_status_enum"),
        nullable=False,
        default=CallStatus.INITIATED,
        index=True,
    )
    from_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Duration & Timing
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Recording & Transcription
    recording_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcription: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI Processing
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # NOTE: attribute renamed from `metadata` (reserved by SQLAlchemy declarative);
    # the underlying DB column stays "metadata".
    call_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )

    # Cost Tracking
    cost_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="calls")
    contact: Mapped[Contact | None] = relationship("Contact", lazy="noload")
    summary: Mapped[CallSummary | None] = relationship(
        "CallSummary", back_populates="call", uselist=False, lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Call(id={self.id}, status={self.status}, direction={self.direction})>"
