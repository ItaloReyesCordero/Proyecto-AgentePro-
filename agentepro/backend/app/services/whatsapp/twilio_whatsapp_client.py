from __future__ import annotations

import asyncio

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioWhatsAppClient:
    """Envía mensajes de WhatsApp a través de Twilio (en vez de Meta directo).

    Expone la MISMA interfaz que `WhatsAppClient` (send_text / mark_as_read /
    send_typing_indicator) para poder usarse en el mismo pipeline de mensajería.
    `mark_as_read` y `send_typing_indicator` son no-ops (Twilio no los soporta).

    El número `from_number` debe venir en formato Twilio (p. ej.
    "whatsapp:+14155238886" para el Sandbox, o el número del negocio en producción).
    """

    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number if from_number.startswith("whatsapp:") else f"whatsapp:{from_number}"

    async def send_text(self, to: str, text: str) -> None:
        to_wa = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                url,
                auth=(self.account_sid, self.auth_token),
                data={"From": self.from_number, "To": to_wa, "Body": text},
            )
            if resp.status_code >= 400:
                logger.error("twilio_whatsapp_send_failed", status=resp.status_code, body=resp.text[:300])
                resp.raise_for_status()

    async def mark_as_read(self, *_args, **_kwargs) -> None:  # noqa: D401 (no-op)
        # Twilio auto-marca como leído; no-op async para igualar la interfaz de Meta.
        await asyncio.sleep(0)
        return None

    async def send_typing_indicator(self, *_args, **_kwargs) -> None:  # noqa: D401 (no-op)
        # Twilio no soporta indicador de escritura; no-op async para igualar la interfaz.
        await asyncio.sleep(0)
        return None
