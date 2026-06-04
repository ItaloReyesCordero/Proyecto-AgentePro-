"""Tests unitarios del parser de payloads de WhatsApp (Meta Graph)."""
from __future__ import annotations

from typing import Any

import pytest

from app.services.whatsapp.message_parser import parse_messages, parse_statuses


def _envelope(messages: list[dict[str, Any]], contacts: list[dict[str, Any]] | None = None) -> dict:
    """Envuelve mensajes en la estructura anidada entry→changes→value."""
    return {
        "entry": [
            {
                "changes": [
                    {"value": {"messages": messages, "contacts": contacts or []}}
                ]
            }
        ]
    }


def test_parse_text_message():
    payload = _envelope(
        [{"id": "wamid.1", "from": "51999", "type": "text", "text": {"body": "hola"}}],
        [{"wa_id": "51999", "profile": {"name": "Ana"}}],
    )
    msgs = parse_messages(payload)
    assert len(msgs) == 1
    m = msgs[0]
    assert m.wa_message_id == "wamid.1"
    assert m.from_number == "51999"
    assert m.message_type == "text"
    assert m.text == "hola"
    assert m.contact_name == "Ana"
    assert m.media_id is None


def test_parse_audio_message_has_media_id_no_text():
    payload = _envelope([{"id": "a1", "from": "51", "type": "audio", "audio": {"id": "media-1"}}])
    m = parse_messages(payload)[0]
    assert m.message_type == "audio"
    assert m.text == ""
    assert m.media_id == "media-1"


def test_parse_image_uses_caption_and_media():
    payload = _envelope(
        [{"id": "i1", "from": "51", "type": "image", "image": {"id": "img-9", "caption": "mira esto"}}]
    )
    m = parse_messages(payload)[0]
    assert m.message_type == "image"
    assert m.text == "mira esto"
    assert m.media_id == "img-9"


def test_parse_document_caption_and_media():
    payload = _envelope(
        [{"id": "d1", "from": "51", "type": "document", "document": {"id": "doc-1", "caption": "factura"}}]
    )
    m = parse_messages(payload)[0]
    assert m.message_type == "document"
    assert m.text == "factura"
    assert m.media_id == "doc-1"


def test_parse_video_maps_to_image_type():
    # Por diseño, el video se normaliza al tipo "image" con su media_id.
    payload = _envelope(
        [{"id": "v1", "from": "51", "type": "video", "video": {"id": "vid-1", "caption": "clip"}}]
    )
    m = parse_messages(payload)[0]
    assert m.message_type == "image"
    assert m.media_id == "vid-1"
    assert m.text == "clip"


def test_parse_sticker():
    payload = _envelope([{"id": "s1", "from": "51", "type": "sticker", "sticker": {"id": "stk-1"}}])
    m = parse_messages(payload)[0]
    assert m.message_type == "sticker"
    assert m.media_id == "stk-1"


def test_parse_button_reply_text():
    payload = _envelope([{"id": "b1", "from": "51", "type": "button", "button": {"text": "Sí"}}])
    m = parse_messages(payload)[0]
    assert m.message_type == "text"
    assert m.text == "Sí"


def test_parse_interactive_button_reply():
    payload = _envelope(
        [
            {
                "id": "x1",
                "from": "51",
                "type": "interactive",
                "interactive": {"button_reply": {"title": "Confirmar"}},
            }
        ]
    )
    m = parse_messages(payload)[0]
    assert m.message_type == "text"
    assert m.text == "Confirmar"


def test_parse_interactive_list_reply():
    payload = _envelope(
        [
            {
                "id": "x2",
                "from": "51",
                "type": "interactive",
                "interactive": {"list_reply": {"title": "Opción A"}},
            }
        ]
    )
    m = parse_messages(payload)[0]
    assert m.text == "Opción A"


def test_parse_unknown_type_returns_type_with_empty_text():
    payload = _envelope([{"id": "u1", "from": "51", "type": "location"}])
    m = parse_messages(payload)[0]
    assert m.message_type == "location"
    assert m.text == ""
    assert m.media_id is None


def test_parse_message_without_matching_contact_name_is_none():
    payload = _envelope([{"id": "n1", "from": "51000", "type": "text", "text": {"body": "hi"}}])
    assert parse_messages(payload)[0].contact_name is None


def test_parse_multiple_messages_preserves_order():
    payload = _envelope(
        [
            {"id": "1", "from": "a", "type": "text", "text": {"body": "uno"}},
            {"id": "2", "from": "b", "type": "text", "text": {"body": "dos"}},
        ]
    )
    msgs = parse_messages(payload)
    assert [m.text for m in msgs] == ["uno", "dos"]


def test_parse_empty_payload_returns_empty_list():
    assert parse_messages({}) == []
    assert parse_messages({"entry": []}) == []


def test_parse_text_missing_body_is_empty_string():
    payload = _envelope([{"id": "t", "from": "51", "type": "text", "text": {}}])
    assert parse_messages(payload)[0].text == ""


def test_parse_defaults_type_to_text_when_absent():
    payload = _envelope([{"id": "t", "from": "51", "text": {"body": "sin tipo"}}])
    m = parse_messages(payload)[0]
    assert m.message_type == "text"
    assert m.text == "sin tipo"


# --- parse_statuses ----------------------------------------------------------


def _status_env(statuses: list[dict[str, Any]]) -> dict:
    return {"entry": [{"changes": [{"value": {"statuses": statuses}}]}]}


@pytest.mark.parametrize("state", ["sent", "delivered", "read", "failed"])
def test_parse_status_states(state):
    payload = _status_env([{"id": "wamid.x", "status": state, "timestamp": "123"}])
    out = parse_statuses(payload)
    assert len(out) == 1
    assert out[0].status == state
    assert out[0].wa_message_id == "wamid.x"
    assert out[0].timestamp == "123"


def test_parse_statuses_empty():
    assert parse_statuses({}) == []
    assert parse_statuses(_status_env([])) == []


def test_parse_statuses_multiple():
    payload = _status_env(
        [{"id": "1", "status": "sent"}, {"id": "2", "status": "read"}]
    )
    out = parse_statuses(payload)
    assert [s.status for s in out] == ["sent", "read"]
