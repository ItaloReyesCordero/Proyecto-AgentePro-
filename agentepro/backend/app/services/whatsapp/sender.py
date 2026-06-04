from __future__ import annotations

from app.config import settings
from app.models.tenant import Tenant
from app.services.whatsapp.client import WhatsAppClient
from app.utils.encryption import decrypt_if_value
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_client_for_tenant(tenant: Tenant) -> WhatsAppClient | None:
    """Construye un WhatsAppClient con las credenciales desencriptadas del tenant."""
    if not tenant.phone_number_id or not tenant.whatsapp_access_token:
        logger.warning("whatsapp_credentials_missing", tenant_id=str(tenant.id))
        return None
    token = decrypt_if_value(tenant.whatsapp_access_token)
    if not token:
        return None
    return WhatsAppClient(phone_number_id=tenant.phone_number_id, access_token=token)


def build_outbound_client(tenant: Tenant):
    """Devuelve el mejor cliente de WhatsApp para ENVIAR a este tenant.

    Prioriza Meta (si el negocio conectó su WhatsApp Cloud API). Si no, cae a
    Twilio usando las credenciales globales + número de envío configurado
    (`TWILIO_WHATSAPP_FROM`, el sandbox por defecto). Así los recordatorios y
    avisos funcionan tanto con Meta como con Twilio.
    """
    meta = build_client_for_tenant(tenant)
    if meta is not None:
        return meta
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_WHATSAPP_FROM:
        from app.services.whatsapp.twilio_whatsapp_client import TwilioWhatsAppClient

        return TwilioWhatsAppClient(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            from_number=settings.TWILIO_WHATSAPP_FROM,
        )
    return None


async def send_whatsapp_message(tenant: Tenant, to: str, text: str) -> bool:
    """Helper de alto nivel para enviar un mensaje de texto a un contacto.

    Usa Meta si está configurado, si no Twilio (ver `build_outbound_client`).
    """
    client = build_outbound_client(tenant)
    if client is None:
        if settings.DEBUG:
            logger.info("whatsapp_send_skipped_debug", to=to, text=text[:80])
            return True
        return False
    try:
        await client.send_text(to=to, text=text)
        return True
    except Exception as exc:
        logger.error("whatsapp_send_failed", tenant_id=str(tenant.id), error=str(exc))
        return False
