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


class WebhookSource(str, enum.Enum):
    META_WHATSAPP = "meta_whatsapp"
    META_INSTAGRAM = "meta_instagram"
    RETELL = "retell"
    TWILIO = "twilio"
    CULQI = "culqi"


class WebhookStatus(str, enum.Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Webhook Details
    source: Mapped[WebhookSource] = mapped_column(
        SAEnum(WebhookSource, name="webhook_source_enum"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Processing
    status: Mapped[WebhookStatus] = mapped_column(
        SAEnum(WebhookStatus, name="webhook_status_enum"),
        nullable=False,
        default=WebhookStatus.RECEIVED,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant | None] = relationship("Tenant", back_populates="webhook_logs")

    def __repr__(self) -> str:
        return f"<WebhookLog(id={self.id}, source={self.source}, event_type={self.event_type}, status={self.status})>"
