from __future__ import annotations
import json
import re
from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.tenant import Tenant
from app.models.agent_config import AgentConfig
from app.models.contact import Contact
from app.services.ai.prompt_builder import build_whatsapp_system_prompt
from app.core.exceptions import PlanLimitExceededError
from app.core.plans import message_limit
from app.utils.logger import get_logger
from dataclasses import dataclass, field
from typing import Any

logger = get_logger(__name__)

META_PATTERN = re.compile(r"<!--META:(.*?)-->", re.DOTALL)
ACTION_PATTERN = re.compile(r"<!--ACTION:(\w+)-->")


@dataclass
class AgentResponse:
    text: str
    intent: str
    confidence: float
    lead_score: int
    lead_stage: str
    actions: list[str]
    appointment_date: str | None
    key_info: dict[str, Any]
    should_escalate: bool
    tokens_used: int


class AIAgentService:
    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    def _parse_meta(self, text: str) -> dict[str, Any]:
        match = META_PATTERN.search(text)
        if not match:
            return {
                "intent": "unknown",
                "confidence": 0.5,
                "lead_score": 30,
                "lead_stage": "cold",
                "actions": [],
                "appointment_date": None,
                "key_info_extracted": {},
            }
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return {
                "intent": "unknown",
                "confidence": 0.5,
                "lead_score": 30,
                "lead_stage": "cold",
                "actions": [],
                "appointment_date": None,
                "key_info_extracted": {},
            }

    def _clean_response(self, text: str) -> str:
        text = META_PATTERN.sub("", text)
        text = ACTION_PATTERN.sub("", text)
        return text.strip()

    def _check_plan_limit(self, tenant: Tenant) -> None:
        limit = message_limit(tenant.plan)
        used = tenant.messages_used_this_month or 0
        if used >= limit:
            raise PlanLimitExceededError("messages")

    async def _get_conversation_context(
        self,
        conversation_id: str,
        db: AsyncSession,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(reversed(result.scalars().all()))

        context: list[dict[str, str]] = []
        for msg in messages:
            role = "user" if msg.direction == "inbound" else "assistant"
            content = msg.transcription or msg.content or ""
            if content:
                context.append({"role": role, "content": content})
        return context

    async def process_whatsapp_message(
        self,
        message_content: str,
        message_type: str,
        conversation: Conversation,
        tenant: Tenant,
        agent_config: AgentConfig,
        db: AsyncSession,
    ) -> AgentResponse:
        self._check_plan_limit(tenant)

        # Adaptar contenido por tipo
        if message_type == "audio":
            message_content = f"[Audio recibido - transcripción: {message_content}]"
        elif message_type == "image":
            message_content = f"[Imagen recibida] {message_content}"
        elif message_type == "document":
            message_content = f"[Documento recibido] {message_content}"
        elif message_type == "sticker":
            message_content = "[Sticker recibido 😊]"

        system_prompt = build_whatsapp_system_prompt(agent_config, channel="whatsapp")
        context_messages = await self._get_conversation_context(
            str(conversation.id), db
        )
        context_messages.append({"role": "user", "content": message_content})

        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                system=system_prompt,
                messages=context_messages,
            )
            raw_text: str = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
        except Exception as exc:
            logger.error(
                "claude_api_error",
                error=str(exc),
                tenant_id=str(tenant.id),
                conversation_id=str(conversation.id),
            )
            return AgentResponse(
                text=(
                    "Disculpe, tuve un problema técnico. "
                    "Por favor intente nuevamente en unos momentos."
                ),
                intent="error",
                confidence=1.0,
                lead_score=conversation.tokens_used or 0,
                lead_stage="cold",
                actions=[],
                appointment_date=None,
                key_info={},
                should_escalate=False,
                tokens_used=0,
            )

        meta = self._parse_meta(raw_text)
        clean_text = self._clean_response(raw_text)
        should_escalate = "<!--ACTION:ESCALATE-->" in raw_text or "ESCALATE" in meta.get(
            "actions", []
        )

        # Incrementar contador de mensajes del tenant
        tenant.messages_used_this_month = (tenant.messages_used_this_month or 0) + 1

        return AgentResponse(
            text=clean_text,
            intent=meta.get("intent", "unknown"),
            confidence=float(meta.get("confidence", 0.5)),
            lead_score=int(meta.get("lead_score", 30)),
            lead_stage=meta.get("lead_stage", "cold"),
            actions=meta.get("actions", []),
            appointment_date=meta.get("appointment_date"),
            key_info=meta.get("key_info_extracted", {}),
            should_escalate=should_escalate,
            tokens_used=tokens_used,
        )

    async def process_instagram_dm(
        self,
        message_content: str,
        conversation: Conversation,
        tenant: Tenant,
        agent_config: AgentConfig,
        db: AsyncSession,
    ) -> AgentResponse:
        """Procesa un DM de Instagram usando el mismo motor que WhatsApp."""
        return await self.process_whatsapp_message(
            message_content=message_content,
            message_type="text",
            conversation=conversation,
            tenant=tenant,
            agent_config=agent_config,
            db=db,
        )

    async def test_message(
        self,
        message_content: str,
        agent_config: AgentConfig,
    ) -> AgentResponse:
        """Procesa un mensaje de prueba sin persistir nada (para el wizard)."""
        system_prompt = build_whatsapp_system_prompt(agent_config, channel="whatsapp")
        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": message_content}],
            )
            raw_text = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
        except Exception as exc:
            logger.error("agent_test_error", error=str(exc))
            return AgentResponse(
                text="No se pudo generar la respuesta de prueba (verifica ANTHROPIC_API_KEY).",
                intent="error",
                confidence=1.0,
                lead_score=0,
                lead_stage="cold",
                actions=[],
                appointment_date=None,
                key_info={},
                should_escalate=False,
                tokens_used=0,
            )
        meta = self._parse_meta(raw_text)
        return AgentResponse(
            text=self._clean_response(raw_text),
            intent=meta.get("intent", "unknown"),
            confidence=float(meta.get("confidence", 0.5)),
            lead_score=int(meta.get("lead_score", 30)),
            lead_stage=meta.get("lead_stage", "cold"),
            actions=meta.get("actions", []),
            appointment_date=meta.get("appointment_date"),
            key_info=meta.get("key_info_extracted", {}),
            should_escalate="ESCALATE" in raw_text,
            tokens_used=tokens_used,
        )

    async def generate_quick_reply(
        self,
        context: str,
        agent_config: AgentConfig,
    ) -> str:
        """Genera una respuesta rápida sin guardar contexto completo."""
        system_prompt = build_whatsapp_system_prompt(agent_config)
        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL_DEFAULT,
                max_tokens=256,
                system=system_prompt,
                messages=[{"role": "user", "content": context}],
            )
            raw = response.content[0].text
            return self._clean_response(raw)
        except Exception as exc:
            logger.error("quick_reply_error", error=str(exc))
            return "Gracias por tu mensaje. Te responderemos pronto."
