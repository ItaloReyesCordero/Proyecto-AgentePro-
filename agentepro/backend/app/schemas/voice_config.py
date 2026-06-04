from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict


class VoiceConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    retell_agent_id: str | None
    voice_id: str
    agent_name: str
    welcome_message: str
    direction: str
    max_call_duration_seconds: int
    enable_recording: bool
    enable_transcription: bool
    enable_summary: bool
    outbound_calling_hours: dict[str, Any]
    send_whatsapp_summary: bool
    create_hubspot_task: bool
    escalation_phone: str | None
    language: str
    ambient_sound: str | None


class VoiceConfigUpdate(BaseModel):
    voice_id: str | None = None
    agent_name: str | None = None
    welcome_message: str | None = None
    direction: str | None = None
    max_call_duration_seconds: int | None = None
    enable_recording: bool | None = None
    enable_transcription: bool | None = None
    outbound_calling_hours: dict[str, Any] | None = None
    send_whatsapp_summary: bool | None = None
    create_hubspot_task: bool | None = None
    escalation_phone: str | None = None
    ambient_sound: str | None = None
