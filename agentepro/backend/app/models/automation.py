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
    from app.models.automation_run import AutomationRun


class AutomationType(str, enum.Enum):
    BROADCAST = "broadcast"
    DRIP_CAMPAIGN = "drip_campaign"
    FOLLOW_UP = "follow_up"
    LEAD_NURTURING = "lead_nurturing"
    REACTIVATION = "reactivation"
    APPOINTMENT_REMINDER = "appointment_reminder"
    CUSTOM = "custom"


class AutomationStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AutomationTriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"


class Automation(Base):
    __tablename__ = "automations"

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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    automation_type: Mapped[AutomationType] = mapped_column(
        SAEnum(AutomationType, name="automation_type_enum"),
        nullable=False,
        default=AutomationType.BROADCAST,
    )

    # Status
    status: Mapped[AutomationStatus] = mapped_column(
        SAEnum(AutomationStatus, name="automation_status_enum"),
        nullable=False,
        default=AutomationStatus.DRAFT,
        index=True,
    )

    # Trigger Configuration
    trigger_type: Mapped[AutomationTriggerType] = mapped_column(
        SAEnum(AutomationTriggerType, name="automation_trigger_type_enum"),
        nullable=False,
        default=AutomationTriggerType.MANUAL,
    )
    trigger_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Target Audience
    target_filter: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    target_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    target_status: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Workflow / Steps
    steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    # Message Template
    message_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_variables: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Limits & Throttling
    daily_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rate_limit_per_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    respect_business_hours: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Statistics
    total_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_contacts_reached: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_messages_sent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_responses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamps
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="automations")
    runs: Mapped[list[AutomationRun]] = relationship(
        "AutomationRun", back_populates="automation", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Automation(id={self.id}, name={self.name}, status={self.status})>"
