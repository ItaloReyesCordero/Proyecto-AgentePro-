from __future__ import annotations

from typing import Any

from app.schemas.webhook_meta import ParsedStatusUpdate, ParsedWhatsAppMessage


def _extract_text(message: dict[str, Any]) -> tuple[str, str, str | None]:
    """Devuelve (message_type, text, media_id) según el tipo de mensaje."""
    msg_type = message.get("type", "text")
    if msg_type == "text":
        return "text", message.get("text", {}).get("body", ""), None
    if msg_type == "audio":
        return "audio", "", message.get("audio", {}).get("id")
    if msg_type == "image":
        caption = message.get("image", {}).get("caption", "")
        return "image", caption, message.get("image", {}).get("id")
    if msg_type == "document":
        caption = message.get("document", {}).get("caption", "")
        return "document", caption, message.get("document", {}).get("id")
    if msg_type == "video":
        caption = message.get("video", {}).get("caption", "")
        return "image", caption, message.get("video", {}).get("id")
    if msg_type == "sticker":
        return "sticker", "", message.get("sticker", {}).get("id")
    if msg_type == "button":
        return "text", message.get("button", {}).get("text", ""), None
    if msg_type == "interactive":
        interactive = message.get("interactive", {})
        reply = interactive.get("button_reply") or interactive.get("list_reply") or {}
        return "text", reply.get("title", ""), None
    return msg_type, "", None


def parse_messages(payload: dict[str, Any]) -> list[ParsedWhatsAppMessage]:
    """Aplana el payload anidado de Meta a una lista de mensajes normalizados."""
    parsed: list[ParsedWhatsAppMessage] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = {c.get("wa_id"): c for c in value.get("contacts", [])}
            for message in value.get("messages", []):
                msg_type, text, media_id = _extract_text(message)
                wa_id = message.get("from", "")
                contact = contacts.get(wa_id, {})
                profile_name = contact.get("profile", {}).get("name")
                parsed.append(
                    ParsedWhatsAppMessage(
                        wa_message_id=message.get("id", ""),
                        from_number=wa_id,
                        wa_id=wa_id,
                        contact_name=profile_name,
                        message_type=msg_type,
                        text=text,
                        media_id=media_id,
                        timestamp=message.get("timestamp"),
                        raw=message,
                    )
                )
    return parsed


def parse_statuses(payload: dict[str, Any]) -> list[ParsedStatusUpdate]:
    """Extrae actualizaciones de estado (delivered/read/failed)."""
    statuses: list[ParsedStatusUpdate] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for status in value.get("statuses", []):
                statuses.append(
                    ParsedStatusUpdate(
                        wa_message_id=status.get("id", ""),
                        status=status.get("status", ""),
                        timestamp=status.get("timestamp"),
                    )
                )
    return statuses
