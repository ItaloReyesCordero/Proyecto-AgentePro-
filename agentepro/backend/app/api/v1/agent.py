from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import CurrentTenant, DbSession
from app.models.agent_config import AgentConfig
from app.models.voice_config import VoiceConfig
from app.schemas.agent_config import (
    AgentConfigOut,
    AgentConfigUpdate,
    PromptPreviewResponse,
    TestAgentRequest,
    TestAgentResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.voice_config import VoiceConfigOut, VoiceConfigUpdate
from app.services.ai.agent import AIAgentService
from app.services.ai.prompt_builder import build_whatsapp_system_prompt
from app.services.voice.retell_client import RetellClient

router = APIRouter(prefix="/agent", tags=["agent"])

_agent = AIAgentService()


async def _get_config(db: DbSession, tenant_id) -> AgentConfig:
    result = await db.execute(select(AgentConfig).where(AgentConfig.tenant_id == tenant_id))
    config = result.scalar_one_or_none()
    if config is None:
        config = AgentConfig(tenant_id=tenant_id)
        db.add(config)
        await db.flush()
        # Carga los valores generados por la BD (created_at/updated_at) en el
        # contexto async para evitar un lazy-load posterior fuera del greenlet.
        await db.refresh(config)
    return config


async def _get_voice(db: DbSession, tenant_id) -> VoiceConfig:
    result = await db.execute(select(VoiceConfig).where(VoiceConfig.tenant_id == tenant_id))
    config = result.scalar_one_or_none()
    if config is None:
        config = VoiceConfig(tenant_id=tenant_id)
        db.add(config)
        await db.flush()
    return config


@router.get("/config", response_model=AgentConfigOut)
async def get_config(tenant: CurrentTenant, db: DbSession) -> AgentConfig:
    return await _get_config(db, tenant.id)


@router.put("/config", response_model=AgentConfigOut)
@router.patch("/config", response_model=AgentConfigOut)
async def update_config(
    payload: AgentConfigUpdate, tenant: CurrentTenant, db: DbSession
) -> AgentConfig:
    config = await _get_config(db, tenant.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    await db.flush()
    # `updated_at` (onupdate=func.now()) queda expirado tras el flush; lo
    # recargamos dentro del contexto async para que la serialización de la
    # respuesta no dispare un lazy-load fuera del greenlet (MissingGreenlet).
    await db.refresh(config)
    return config


@router.post("/config/test", response_model=TestAgentResponse)
async def test_config(
    payload: TestAgentRequest, tenant: CurrentTenant, db: DbSession
) -> TestAgentResponse:
    config = await _get_config(db, tenant.id)
    response = await _agent.test_message(payload.message, config)
    return TestAgentResponse(
        reply=response.text,
        intent=response.intent,
        confidence=response.confidence,
        lead_score=response.lead_score,
        lead_stage=response.lead_stage,
        should_escalate=response.should_escalate,
    )


@router.get("/config/preview", response_model=PromptPreviewResponse)
async def preview_prompt(tenant: CurrentTenant, db: DbSession) -> PromptPreviewResponse:
    config = await _get_config(db, tenant.id)
    return PromptPreviewResponse(system_prompt=build_whatsapp_system_prompt(config))


@router.get("/voice", response_model=VoiceConfigOut)
async def get_voice(tenant: CurrentTenant, db: DbSession) -> VoiceConfig:
    return await _get_voice(db, tenant.id)


@router.put("/voice", response_model=VoiceConfigOut)
async def update_voice(
    payload: VoiceConfigUpdate, tenant: CurrentTenant, db: DbSession
) -> VoiceConfig:
    config = await _get_voice(db, tenant.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    await db.flush()
    # Si hay agente Retell, actualiza el prompt
    if tenant.retell_agent_id:
        agent_config = await _get_config(db, tenant.id)
        from app.services.ai.voice_prompt_builder import build_voice_system_prompt

        prompt = build_voice_system_prompt(config, agent_config, "inbound")
        try:
            await RetellClient().update_agent(tenant.retell_agent_id, {"general_prompt": prompt})
        except Exception:
            pass
    return config


@router.post("/voice/test-call", response_model=MessageResponse)
async def test_call(tenant: CurrentTenant, db: DbSession) -> MessageResponse:
    if not tenant.retell_agent_id or not tenant.twilio_phone_number:
        raise HTTPException(status_code=400, detail="Agente de voz no provisionado")
    return MessageResponse(message="Llamada de prueba encolada")
