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


class VoiceCallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BOTH = "both"


class VoiceConfig(Base):
    __tablename__ = "voice_configs"

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

    # Retell / Voice Identity
    retell_agent_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    voice_id: Mapped[str] = mapped_column(String(100), nullable=False, default="es-ES-ElviraNeural")
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, default="Asistente de Voz")
    welcome_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Hola, gracias por llamar. ¿En qué puedo ayudarte?",
    )
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Call Behavior
    direction: Mapped[VoiceCallDirection] = mapped_column(
        SAEnum(VoiceCallDirection, name="voice_call_direction_enum"),
        nullable=False,
        default=VoiceCallDirection.INBOUND,
    )
    max_call_duration_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=600
    )
    enable_recording: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enable_transcription: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enable_summary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Outbound Calling Configuration
    outbound_calling_hours: Mapped[dict[str, Any]] = mapped_column(
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
    max_retry_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    # Post-call Actions
    send_whatsapp_summary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    create_hubspot_task: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalation_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # AI Parameters
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    ambient_sound: Mapped[str | None] = mapped_column(String(50), nullable=True)
    responsiveness: Mapped[float] = mapped_column(nullable=False, default=1.0)
    interruption_sensitivity: Mapped[float] = mapped_column(nullable=False, default=1.0)
    enable_backchannel: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="voice_config")

    def __repr__(self) -> str:
        return f"<VoiceConfig(id={self.id}, tenant_id={self.tenant_id}, voice_id={self.voice_id})>"
