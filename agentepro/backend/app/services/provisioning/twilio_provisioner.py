from __future__ import annotations

from app.config import settings
from app.services.voice.twilio_client import TwilioClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


def provision_phone_number(tenant_slug: str) -> str | None:
    """Compra y configura un número Twilio para el tenant.

    Devuelve el número (E.164) o None si Twilio no está habilitado.
    """
    client = TwilioClient()
    if not client.enabled:
        logger.info("twilio_provision_skipped", tenant=tenant_slug)
        return settings.TWILIO_DEFAULT_PHONE_NUMBER or None

    number = client.purchase_number(country="PE", area_code="1")
    if not number:
        number = client.purchase_number(country="US")
    if not number:
        return None

    webhook_url = f"{_backend_base()}/webhooks/twilio/voice/{tenant_slug}"
    client.configure_voice_webhook(number, webhook_url)
    return number


def release_phone_number(number: str) -> None:
    client = TwilioClient()
    if client.enabled and number:
        client.release_number(number)


def _backend_base() -> str:
    # En producción esto debe apuntar al dominio público del backend.
    return settings.FRONTEND_URL.replace(":5173", ":8000")
