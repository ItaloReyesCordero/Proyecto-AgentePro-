from __future__ import annotations

import re

from fastapi import APIRouter, BackgroundTasks, Request, Response
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.schemas.webhook_meta import ParsedWhatsAppMessage
from app.services.whatsapp.twilio_whatsapp_client import TwilioWhatsAppClient
from app.services.whatsapp.webhook_handler import handle_inbound_message
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["webhooks"])

_EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'


def _strip_wa(value: str) -> str:
    """'whatsapp:+51916085873' -> '+51916085873'."""
    return value.replace("whatsapp:", "").strip()


async def _process(tenant_slug: str, form: dict[str, str]) -> None:
    """Procesa el mensaje entrante de Twilio WhatsApp en segundo plano."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
            tenant = result.scalar_one_or_none()
            if tenant is None or not tenant.is_active:
                return

            from_raw = form.get("From", "")
            to_raw = form.get("To", "")  # el número del negocio (responderemos desde aquí)
            from_number = _strip_wa(from_raw)
            wa_id = re.sub(r"\D", "", from_number)  # solo dígitos, estilo Meta

            # ¿Es nota de voz? -> el handler responde pidiendo que escriban.
            num_media = int(form.get("NumMedia", "0") or "0")
            media_type = form.get("MediaContentType0", "") if num_media else ""
            message_type = "audio" if media_type.startswith("audio") else "text"

            parsed = ParsedWhatsAppMessage(
                wa_message_id=form.get("MessageSid", ""),
                from_number=from_number,
                wa_id=wa_id,
                contact_name=form.get("ProfileName") or None,
                message_type=message_type,
                text=form.get("Body", "") or "",
                raw=dict(form),
            )

            # Cliente Twilio para responder desde el MISMO número que escribió el cliente.
            client = TwilioWhatsAppClient(
                account_sid=settings.TWILIO_ACCOUNT_SID,
                auth_token=settings.TWILIO_AUTH_TOKEN,
                from_number=to_raw,
            )
            await handle_inbound_message(
                db, tenant, parsed, channel="whatsapp", client_override=client
            )
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("twilio_whatsapp_processing_error", error=str(exc), tenant=tenant_slug)


@router.post("/twilio/whatsapp/{tenant_slug}")
async def receive_twilio_whatsapp(
    tenant_slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    """Recibe mensajes de WhatsApp enviados a través de Twilio (incl. el Sandbox).

    Twilio manda los datos como formulario (Body, From, To, MessageSid, ...).
    Respondemos 200 al instante y procesamos en segundo plano.
    """
    form = await request.form()
    data = {k: str(v) for k, v in form.items()}
    background_tasks.add_task(_process, tenant_slug, data)
    return Response(content=_EMPTY_TWIML, media_type="application/xml", status_code=200)
