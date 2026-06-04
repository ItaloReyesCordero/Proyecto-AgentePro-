from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AgentConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    agent_name: str
    welcome_message: str
    language: str
    business_hours: dict[str, Any]
    outside_hours_message: str
    faqs: list[dict[str, Any]]
    services: list[dict[str, Any]]
    escalation_keywords: list[str]
    escalation_message: str
    escalation_phone: str | None
    escalation_email: str | None
    owner_contacts: list[str]
    owner_handoff_message: str
    lead_qualification_questions: list[dict[str, Any]]
    auto_qualify_leads: bool
    temperature: float
    max_response_length: int
    enable_audio_transcription: bool
    auto_create_hubspot_contacts: bool
    auto_create_hubspot_deals: bool
    updated_at: datetime


class AgentConfigUpdate(BaseModel):
    agent_name: str | None = None
    welcome_message: str | None = None
    language: str | None = None
    business_hours: dict[str, Any] | None = None
    outside_hours_message: str | None = None
    faqs: list[dict[str, Any]] | None = None
    services: list[dict[str, Any]] | None = None
    escalation_keywords: list[str] | None = None
    escalation_message: str | None = None
    escalation_phone: str | None = None
    escalation_email: str | None = None
    owner_contacts: list[str] | None = None
    owner_handoff_message: str | None = None
    lead_qualification_questions: list[dict[str, Any]] | None = None
    auto_qualify_leads: bool | None = None
    temperature: float | None = None
    max_response_length: int | None = None
    enable_audio_transcription: bool | None = None
    auto_create_hubspot_contacts: bool | None = None
    auto_create_hubspot_deals: bool | None = None


class TestAgentRequest(BaseModel):
    message: str


class TestAgentResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    lead_score: int
    lead_stage: str
    should_escalate: bool


class PromptPreviewResponse(BaseModel):
    system_prompt: str
