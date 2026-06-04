from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class HubspotEntityType(str, enum.Enum):
    CONTACT = "contact"
    DEAL = "deal"
    TASK = "task"
    NOTE = "note"


class HubspotAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class HubspotSyncStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class HubspotSyncLog(Base):
    __tablename__ = "hubspot_sync_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Sync Details
    entity_type: Mapped[HubspotEntityType] = mapped_column(
        SAEnum(HubspotEntityType, name="hubspot_entity_type_enum"),
        nullable=False,
    )
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    hubspot_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[HubspotAction] = mapped_column(
        SAEnum(HubspotAction, name="hubspot_action_enum"),
        nullable=False,
    )
    status: Mapped[HubspotSyncStatus] = mapped_column(
        SAEnum(HubspotSyncStatus, name="hubspot_sync_status_enum"),
        nullable=False,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="hubspot_sync_logs")

    def __repr__(self) -> str:
        return f"<HubspotSyncLog(id={self.id}, entity_type={self.entity_type}, action={self.action}, status={self.status})>"
