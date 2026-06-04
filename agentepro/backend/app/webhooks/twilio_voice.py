from __future__ import annotations

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from app.core.plans import FEATURE_VOICE, call_limit, plan_has_feature
from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.services import call_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["webhooks"])

_TWIML_REJECT = """<?xml version="1.0" encoding="UTF-8"?>
<Response><Say language="es-MX">Lo sentimos, este servicio no está disponible.</Say><Hangup/></Response>"""


@router.post("/twilio/voice/{tenant_slug}")
async def twilio_incoming_call(tenant_slug: str, request: Request) -> Response:
    """Devuelve TwiML que conecta la llamada entrante al agente de voz de Retell."""
    form = await request.form()
    from_number = str(form.get("From", ""))
    to_number = str(form.get("To", ""))
    call_sid = str(form.get("CallSid", ""))

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
        tenant = result.scalar_one_or_none()
        if tenant is None or not tenant.is_active or not tenant.retell_agent_id:
            return Response(content=_TWIML_REJECT, media_type="application/xml")
        # Protección de costos: no atender si la cuenta está bloqueada (prueba
        # vencida / suspendida), si el plan no incluye voz, o si ya se alcanzó el
        # tope de llamadas del mes.
        if (
            tenant.service_blocked
            or not plan_has_feature(tenant.plan, FEATURE_VOICE)
            or (tenant.calls_used_this_month or 0) >= call_limit(tenant.plan)
        ):
            return Response(content=_TWIML_REJECT, media_type="application/xml")
        try:
            await call_service.create_call(
                db,
                tenant_id=tenant.id,
                twilio_call_sid=call_sid,
                direction="inbound",
                from_number=from_number,
                to_number=to_number,
            )
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("twilio_call_record_failed", error=str(exc))

        retell_agent_id = tenant.retell_agent_id

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://api.retellai.com/audio-websocket/{retell_agent_id}">
      <Parameter name="tenant_slug" value="{tenant_slug}"/>
      <Parameter name="from_number" value="{from_number}"/>
    </Stream>
  </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")
