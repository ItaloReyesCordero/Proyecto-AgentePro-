from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.plans import FEATURE_VOICE, call_limit, plan_has_feature
from app.models.call import Call, CallDirection, CallStatus
from app.models.contact import Contact
from app.models.tenant import Tenant
from app.models.voice_config import VoiceConfig
from app.services import call_service
from app.services.voice.retell_client import RetellClient
from app.utils.helpers import is_within_business_hours
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OutboundCallError(Exception):
    pass


async def call_lead(
    db: AsyncSession,
    tenant: Tenant,
    contact: Contact,
    reason: str = "follow_up",
) -> Call:
    """Lanza una llamada saliente a un lead tras validar todas las precondiciones."""
    if tenant.service_blocked or not tenant.is_active:
        raise OutboundCallError("La cuenta está bloqueada (prueba vencida, suspendida por pago o inactiva).")

    if not plan_has_feature(tenant.plan, FEATURE_VOICE):
        raise OutboundCallError("Tu plan no incluye el módulo de voz/llamadas.")
    if (tenant.calls_used_this_month or 0) >= call_limit(tenant.plan):
        raise OutboundCallError("Límite de llamadas del plan alcanzado.")

    if not contact.opted_in:
        raise OutboundCallError("El contacto está marcado como 'no contactar'.")

    result = await db.execute(select(VoiceConfig).where(VoiceConfig.tenant_id == tenant.id))
    voice_config = result.scalar_one_or_none()
    if voice_config is None:
        raise OutboundCallError("El tenant no tiene configuración de voz.")

    if not is_within_business_hours(voice_config.outbound_calling_hours or {}):
        raise OutboundCallError("Fuera del horario permitido para llamadas salientes.")

    # No llamar si ya se le llamó en las últimas 4 horas
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=4)
    recent = await db.execute(
        select(Call).where(
            Call.tenant_id == tenant.id,
            Call.contact_id == contact.id,
            Call.direction == CallDirection.OUTBOUND,
            Call.created_at >= cutoff,
        )
    )
    if recent.scalars().first():
        raise OutboundCallError("Ya se contactó a este lead en las últimas 4 horas.")

    to_number = contact.phone_number or contact.wa_id
    if not to_number:
        raise OutboundCallError("El contacto no tiene número telefónico.")

    call = await call_service.create_call(
        db,
        tenant_id=tenant.id,
        direction="outbound",
        from_number=tenant.twilio_phone_number,
        to_number=to_number,
        contact_id=contact.id,
        status=CallStatus.INITIATED,
    )

    if tenant.retell_agent_id and tenant.twilio_phone_number:
        client = RetellClient()
        result_call = await client.create_phone_call(
            from_number=tenant.twilio_phone_number,
            to_number=to_number,
            agent_id=tenant.retell_agent_id,
            metadata={"contact_id": str(contact.id), "reason": reason},
        )
        if result_call and result_call.get("call_id"):
            call.retell_call_id = result_call["call_id"]
            await db.flush()
    else:
        logger.info("outbound_call_simulated", contact_id=str(contact.id), reason=reason)

    tenant.calls_used_this_month = (tenant.calls_used_this_month or 0) + 1
    return call
