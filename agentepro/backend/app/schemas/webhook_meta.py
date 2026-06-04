from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ParsedWhatsAppMessage(BaseModel):
    """Mensaje de WhatsApp normalizado desde el payload anidado de Meta."""

    wa_message_id: str
    from_number: str
    wa_id: str
    contact_name: str | None
    message_type: str
    text: str
    media_id: str | None = None
    media_url: str | None = None
    timestamp: str | None = None
    raw: dict[str, Any] = {}


class ParsedStatusUpdate(BaseModel):
    wa_message_id: str
    status: str  # sent | delivered | read | failed
    timestamp: str | None = None
