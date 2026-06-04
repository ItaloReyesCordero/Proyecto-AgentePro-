from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Agent Identity
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, default="Asistente")
    welcome_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Hola, soy tu asistente virtual. ¿En qué puedo ayudarte?",
    )
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="es")

    # Behavior Configuration
    business_hours: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "lunes": {"active": True, "open": "09:00", "close": "18:00"},
            "martes": {"active": True, "open": "09:00", "close": "18:00"},
            "miercoles": {"active": True, "open": "09:00", "close": "18:00"},
            "jueves": {"active": True, "open": "09:00", "close": "18:00"},
            "viernes": {"active": True, "open": "09:00", "close": "18:00"},
            "sabado": {"active": False, "open": "09:00", "close": "13:00"},
            "domingo": {"active": False, "open": "09:00", "close": "13:00"},
        },
    )
    outside_hours_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Gracias por escribirnos. Estamos fuera de horario. Te responderemos pronto.",
    )

    # FAQs and Knowledge Base
    faqs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    services: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    # Escalation
    escalation_keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: ["hablar con humano", "agente", "persona", "ayuda urgente"],
    )
    escalation_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Te estoy conectando con un agente humano. Por favor espera.",
    )
    escalation_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    escalation_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # "Pasar con el dueño": números de amigos/familiares del dueño. Si uno de
    # ellos escribe, el bot NO responde como asistente: manda un mensaje fijo de
    # "te paso con el dueño" (0 tokens de Claude) y le avisa al dueño.
    owner_contacts: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    owner_handoff_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=(
            "¡Hola! 😊 Para este tema te comunico directamente con el dueño. "
            "En un momento te contactará personalmente."
        ),
    )

    # Lead Qualification
    lead_qualification_questions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    auto_qualify_leads: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # AI Parameters
    temperature: Mapped[float] = mapped_column(nullable=False, default=0.7)
    max_response_length: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    enable_audio_transcription: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enable_image_analysis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # HubSpot Integration
    auto_create_hubspot_contacts: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    auto_create_hubspot_deals: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="agent_config")

    def __repr__(self) -> str:
        return f"<AgentConfig(id={self.id}, tenant_id={self.tenant_id}, agent_name={self.agent_name})>"
