from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_config import AgentConfig
from app.models.message import MessageDirection, MessageType, SenderType
from app.models.tenant import Tenant
from app.schemas.webhook_meta import ParsedWhatsAppMessage
from app.models.appointment import AppointmentSource
from app.services import appointment_service, contact_service, conversation_service
from app.services.ai.agent import AIAgentService
from app.services.crm.contact_sync import sync_contact_to_hubspot
from app.services.crm.deal_manager import create_deal_for_hot_lead
from app.services.notification_service import emit_event, notify_escalation
from app.services.whatsapp.sender import build_client_for_tenant
from app.utils.helpers import phone_matches_any
from app.utils.logger import get_logger

logger = get_logger(__name__)

_agent = AIAgentService()

_MSG_TYPE_MAP = {
    "text": MessageType.TEXT,
    "audio": MessageType.AUDIO,
    "image": MessageType.IMAGE,
    "document": MessageType.DOCUMENT,
    "sticker": MessageType.TEXT,
}


async def handle_inbound_message(
    db: AsyncSession,
    tenant: Tenant,
    parsed: ParsedWhatsAppMessage,
    channel: str = "whatsapp",
    client_override=None,
) -> None:
    """Procesa un mensaje entrante de WhatsApp/Instagram de extremo a extremo.

    `client_override`: si se pasa (p. ej. un TwilioWhatsAppClient), se usa ese
    cliente para responder en vez del de Meta. Permite conectar WhatsApp por
    Twilio sin tocar el resto del flujo.
    """
    # 1. Anti-duplicado
    if parsed.wa_message_id and await conversation_service.find_message_by_wa_id(
        db, parsed.wa_message_id
    ):
        logger.info("duplicate_message_ignored", wa_message_id=parsed.wa_message_id)
        return

    # 2. Agent config
    result = await db.execute(select(AgentConfig).where(AgentConfig.tenant_id == tenant.id))
    agent_config = result.scalar_one_or_none()
    if agent_config is None:
        logger.warning("agent_config_missing", tenant_id=str(tenant.id))
        return

    # 3. Contacto + conversación
    contact = await contact_service.get_or_create_contact(
        db, tenant.id, parsed.wa_id, parsed.contact_name, channel
    )
    contact.total_messages = (contact.total_messages or 0) + 1
    conversation = await conversation_service.get_or_create_open_conversation(
        db, tenant.id, contact, channel
    )

    # 4. Cliente de envío + marcar leído (Twilio si viene override, si no Meta)
    client = client_override or build_client_for_tenant(tenant)
    if client and parsed.wa_message_id:
        await client.mark_as_read(parsed.wa_message_id)
        await client.send_typing_indicator(parsed.wa_message_id)

    # 5. Guardar mensaje entrante
    inbound_text = parsed.text or f"[{parsed.message_type}]"
    await conversation_service.save_message(
        db,
        conversation=conversation,
        tenant_id=tenant.id,
        direction=MessageDirection.INBOUND,
        sender_type=SenderType.CONTACT,
        content=inbound_text,
        message_type=_MSG_TYPE_MAP.get(parsed.message_type, MessageType.TEXT),
        wa_message_id=parsed.wa_message_id,
    )
    await emit_event(
        str(tenant.id),
        "new_message",
        {
            "conversation_id": str(conversation.id),
            "message": {"content": inbound_text, "sender_type": "contact"},
        },
    )

    # 6. Si el bot no está activo (humano tomó control), no responder
    if not conversation_service.is_bot_active(conversation):
        logger.info("bot_inactive_skip", conversation_id=str(conversation.id))
        return

    # 6.5. Si el trial venció, el negocio está suspendido por pago o inactivo, el
    # agente no responde. El mensaje entrante ya quedó guardado para que el dueño lo
    # vea al regularizar.
    if tenant.service_blocked or not tenant.is_active:
        logger.info("tenant_blocked_no_ai_reply", tenant_id=str(tenant.id))
        return

    # 6.7. Notas de voz: NO transcribimos audio (evita el costo de un motor de voz
    # a texto externo). Respondemos pidiendo que lo escriban, SIN llamar a la IA, así
    # no se gastan tokens de Claude. Aplica también a Instagram (mismo pipeline).
    if parsed.message_type == "audio":
        audio_reply = (
            "¡Hola! 🙏 Por ahora no puedo escuchar notas de voz. "
            "¿Me lo puedes escribir en un mensaje, por favor? Así te ayudo enseguida. 😊"
        )
        if client:
            try:
                await client.send_text(to=parsed.from_number, text=audio_reply)
            except Exception as exc:
                logger.error("whatsapp_reply_failed", error=str(exc))
        await conversation_service.save_message(
            db,
            conversation=conversation,
            tenant_id=tenant.id,
            direction=MessageDirection.OUTBOUND,
            sender_type=SenderType.AI,
            content=audio_reply,
        )
        await emit_event(
            str(tenant.id),
            "agent_response",
            {
                "conversation_id": str(conversation.id),
                "message": {"content": audio_reply, "sender_type": "ai"},
            },
        )
        logger.info("audio_message_unsupported_reply", conversation_id=str(conversation.id))
        return

    # 6.8. "Pasar con el dueño": si quien escribe es un amigo/familiar del dueño
    # (número en owner_contacts), NO respondemos como asistente. Mandamos un
    # mensaje fijo de derivación (0 tokens de Claude) y avisamos al dueño para que
    # lo atienda personalmente.
    if phone_matches_any(parsed.from_number or parsed.wa_id, agent_config.owner_contacts):
        handoff_text = agent_config.owner_handoff_message or (
            "¡Hola! 😊 Te comunico directamente con el dueño. En un momento te contactará."
        )
        if client:
            try:
                await client.send_text(to=parsed.from_number, text=handoff_text)
            except Exception as exc:
                logger.error("whatsapp_reply_failed", error=str(exc))
        await conversation_service.save_message(
            db,
            conversation=conversation,
            tenant_id=tenant.id,
            direction=MessageDirection.OUTBOUND,
            sender_type=SenderType.AI,
            content=handoff_text,
        )
        # Marca la conversación como escalada y avisa al dueño (panel + email).
        await conversation_service.escalate(db, conversation)
        await notify_escalation(
            str(tenant.id),
            conversation_id=str(conversation.id),
            contact_name=contact.full_name or parsed.wa_id,
            reason="Contacto conocido del dueño (lista 'pasar con el dueño'). Atiéndelo personalmente.",
            escalation_email=agent_config.escalation_email,
        )
        await emit_event(
            str(tenant.id),
            "agent_response",
            {
                "conversation_id": str(conversation.id),
                "message": {"content": handoff_text, "sender_type": "ai"},
            },
        )
        logger.info("owner_handoff_reply", conversation_id=str(conversation.id))
        return

    await emit_event(str(tenant.id), "agent_typing", {"conversation_id": str(conversation.id)})

    # 7. Procesar con IA
    response = await _agent.process_whatsapp_message(
        message_content=parsed.text,
        message_type=parsed.message_type,
        conversation=conversation,
        tenant=tenant,
        agent_config=agent_config,
        db=db,
    )

    # 8. Enviar respuesta
    if client:
        try:
            await client.send_text(to=parsed.from_number, text=response.text)
        except Exception as exc:
            logger.error("whatsapp_reply_failed", error=str(exc))

    # 9. Guardar mensaje saliente
    await conversation_service.save_message(
        db,
        conversation=conversation,
        tenant_id=tenant.id,
        direction=MessageDirection.OUTBOUND,
        sender_type=SenderType.AI,
        content=response.text,
        tokens_used=response.tokens_used,
    )

    # 10. Lead scoring
    contact_service.apply_lead_update(contact, response.lead_score, response.lead_stage)
    await emit_event(
        str(tenant.id),
        "lead_score_updated",
        {
            "contact_id": str(contact.id),
            "new_score": contact.qualification_score,
            "new_stage": response.lead_stage,
        },
    )

    # 10.5. Detección de cita: si el agente detectó intención de agendar, crea/
    # actualiza la cita y avisa al dueño (panel + email + WhatsApp).
    try:
        await appointment_service.maybe_create_from_agent(
            db,
            tenant=tenant,
            contact=contact,
            agent_config=agent_config,
            intent=response.intent,
            appointment_date=response.appointment_date,
            key_info=response.key_info,
            source=(
                AppointmentSource.INSTAGRAM
                if channel == "instagram"
                else AppointmentSource.WHATSAPP
            ),
        )
    except Exception as exc:
        logger.error("appointment_detect_failed", error=str(exc))

    # 11. Escalado
    if response.should_escalate:
        await conversation_service.escalate(db, conversation)
        await notify_escalation(
            str(tenant.id),
            conversation_id=str(conversation.id),
            contact_name=contact.full_name or parsed.wa_id,
            reason="El agente IA detectó que se requiere atención humana.",
            escalation_email=agent_config.escalation_email,
        )

    await emit_event(
        str(tenant.id),
        "agent_response",
        {
            "conversation_id": str(conversation.id),
            "message": {"content": response.text, "sender_type": "ai"},
        },
    )

    # 12. CRM (best-effort)
    if agent_config.auto_create_hubspot_contacts:
        try:
            hubspot_id = await sync_contact_to_hubspot(db, contact, str(tenant.id))
            if (
                agent_config.auto_create_hubspot_deals
                and response.lead_score >= 70
                and hubspot_id
            ):
                await create_deal_for_hot_lead(hubspot_id, tenant.name)
        except Exception as exc:
            logger.error("hubspot_sync_failed", error=str(exc))
