from __future__ import annotations

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioClient:
    """Wrapper sobre el SDK de Twilio para compra y configuración de números."""

    def __init__(self) -> None:
        self._client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client  # import perezoso

                self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            except Exception as exc:  # pragma: no cover
                logger.error("twilio_init_failed", error=str(exc))

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def purchase_number(self, country: str = "PE", area_code: str | None = None) -> str | None:
        """Compra un número telefónico. Cae a USA si no hay números peruanos."""
        if not self._client:
            return None
        try:
            available = self._client.available_phone_numbers(country).local.list(
                limit=1, **({"area_code": area_code} if area_code else {})
            )
            if not available:
                available = self._client.available_phone_numbers("US").local.list(limit=1)
            if not available:
                return None
            purchased = self._client.incoming_phone_numbers.create(
                phone_number=available[0].phone_number
            )
            return purchased.phone_number
        except Exception as exc:
            logger.error("twilio_purchase_failed", error=str(exc))
            return None

    def configure_voice_webhook(self, phone_number: str, webhook_url: str) -> bool:
        """Apunta el webhook de voz entrante del número al backend."""
        if not self._client:
            return False
        try:
            numbers = self._client.incoming_phone_numbers.list(phone_number=phone_number)
            if not numbers:
                return False
            numbers[0].update(voice_url=webhook_url, voice_method="POST")
            return True
        except Exception as exc:
            logger.error("twilio_configure_failed", error=str(exc))
            return False

    def release_number(self, phone_number: str) -> None:
        """Libera (elimina) un número comprado — usado en rollback."""
        if not self._client:
            return
        try:
            numbers = self._client.incoming_phone_numbers.list(phone_number=phone_number)
            for n in numbers:
                n.delete()
        except Exception as exc:  # pragma: no cover
            logger.error("twilio_release_failed", error=str(exc))
