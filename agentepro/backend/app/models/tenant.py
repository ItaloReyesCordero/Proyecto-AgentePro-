from __future__ import annotations
import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.contact import Contact
    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.agent_config import AgentConfig
    from app.models.voice_config import VoiceConfig
    from app.models.call import Call
    from app.models.instagram_post import InstagramPost
    from app.models.automation import Automation
    from app.models.subscription import Subscription
    from app.models.hubspot_sync_log import HubspotSyncLog
    from app.models.webhook_log import WebhookLog


class BusinessType(str, enum.Enum):
    RETAIL = "retail"
    RESTAURANT = "restaurant"
    SERVICES = "services"
    REAL_ESTATE = "real_estate"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ECOMMERCE = "ecommerce"
    OTHER = "other"


class PlanType(str, enum.Enum):
    INICIAL = "inicial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    business_type: Mapped[BusinessType] = mapped_column(
        SAEnum(BusinessType, name="business_type_enum"), nullable=False, default=BusinessType.OTHER
    )

    # WhatsApp / Meta
    phone_number_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    waba_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    whatsapp_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    webhook_verify_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Twilio / Voice
    twilio_phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    retell_agent_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # HubSpot
    hubspot_company_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Notion (CRM / catálogo del negocio). El token se guarda cifrado con Fernet.
    notion_api_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    notion_database_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notion_last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Instagram
    instagram_account_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    instagram_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Plan & Usage
    plan: Mapped[PlanType] = mapped_column(
        SAEnum(PlanType, name="plan_type_enum"), nullable=False, default=PlanType.TRIAL
    )
    messages_used_this_month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calls_used_this_month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_provisioned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cobro manual (sin pasarela): el dueño cobra por adelantado (Yape/transferencia)
    # y confirma el pago desde el panel. `next_payment_due` marca el vencimiento del
    # mes pagado; `billing_suspended` bloquea la plataforma cuando no pagó.
    next_payment_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_payment_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    monthly_amount_pen: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billing_suspended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    users: Mapped[list[User]] = relationship("User", back_populates="tenant", lazy="noload")
    contacts: Mapped[list[Contact]] = relationship("Contact", back_populates="tenant", lazy="noload")
    conversations: Mapped[list[Conversation]] = relationship(
        "Conversation", back_populates="tenant", lazy="noload"
    )
    messages: Mapped[list[Message]] = relationship("Message", back_populates="tenant", lazy="noload")
    agent_config: Mapped[AgentConfig | None] = relationship(
        "AgentConfig", back_populates="tenant", uselist=False, lazy="noload"
    )
    voice_config: Mapped[VoiceConfig | None] = relationship(
        "VoiceConfig", back_populates="tenant", uselist=False, lazy="noload"
    )
    calls: Mapped[list[Call]] = relationship("Call", back_populates="tenant", lazy="noload")
    instagram_posts: Mapped[list[InstagramPost]] = relationship(
        "InstagramPost", back_populates="tenant", lazy="noload"
    )
    automations: Mapped[list[Automation]] = relationship(
        "Automation", back_populates="tenant", lazy="noload"
    )
    subscription: Mapped[Subscription | None] = relationship(
        "Subscription", back_populates="tenant", uselist=False, lazy="noload"
    )
    hubspot_sync_logs: Mapped[list[HubspotSyncLog]] = relationship(
        "HubspotSyncLog", back_populates="tenant", lazy="noload"
    )
    webhook_logs: Mapped[list[WebhookLog]] = relationship(
        "WebhookLog", back_populates="tenant", lazy="noload"
    )

    # Días antes del vencimiento en que se considera "por vencer" (aviso).
    PAYMENT_DUE_SOON_DAYS = 3

    @property
    def is_trial_expired(self) -> bool:
        """True si el tenant está en TRIAL y su `trial_ends_at` ya pasó."""
        if self.plan != PlanType.TRIAL or self.trial_ends_at is None:
            return False
        ends_at = self.trial_ends_at
        if ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)
        return datetime.now(tz=timezone.utc) >= ends_at

    @property
    def payment_due_at(self) -> datetime | None:
        """Fecha de referencia del próximo cobro: fin del trial si está en prueba,
        o `next_payment_due` si ya es un plan pagado."""
        if self.plan == PlanType.TRIAL:
            return self.trial_ends_at
        return self.next_payment_due

    @property
    def payment_state(self) -> str:
        """Estado de cobro derivado: ``suspended`` | ``overdue`` | ``due_soon`` |
        ``trial`` | ``active``. Se usa en el panel del fundador y en el banner del
        negocio (no se persiste para evitar estados inconsistentes)."""
        if self.billing_suspended:
            return "suspended"
        due = self.payment_due_at
        is_trial = self.plan == PlanType.TRIAL
        if due is None:
            return "trial" if is_trial else "active"
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        delta_days = (due - datetime.now(tz=timezone.utc)).total_seconds() / 86400
        if delta_days < 0:
            return "overdue"
        if delta_days <= self.PAYMENT_DUE_SOON_DAYS:
            return "due_soon"
        return "trial" if is_trial else "active"

    @property
    def service_blocked(self) -> bool:
        """True si el negocio NO debe operar: prueba vencida o suspendido por pago."""
        return self.is_trial_expired or self.billing_suspended

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug={self.slug}, plan={self.plan})>"
