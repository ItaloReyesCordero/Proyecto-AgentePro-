from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.schemas.webhook_meta import ParsedWhatsAppMessage
from app.services.whatsapp.webhook_handler import handle_inbound_message
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_instagram_messages(payload: dict[str, Any]) -> list[ParsedWhatsAppMessage]:
    """Normaliza el payload de mensajería de Instagram a mensajes genéricos."""
    parsed: list[ParsedWhatsAppMessage] = []
    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            message = event.get("message", {})
            if message.get("is_echo"):
                continue
            sender_id = event.get("sender", {}).get("id", "")
            text = message.get("text", "")
            mid = message.get("mid", "")
            if not sender_id or not mid:
                continue
            parsed.append(
                ParsedWhatsAppMessage(
                    wa_message_id=mid,
                    from_number=sender_id,
                    wa_id=sender_id,
                    contact_name=None,
                    message_type="text",
                    text=text,
                    raw=event,
                )
            )
    return parsed


async def handle_instagram_dm(db: AsyncSession, tenant: Tenant, parsed: ParsedWhatsAppMessage) -> None:
    """Reutiliza el pipeline de WhatsApp con canal Instagram."""
    await handle_inbound_message(db, tenant, parsed, channel="instagram")
