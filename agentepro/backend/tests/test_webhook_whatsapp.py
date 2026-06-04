from __future__ import annotations

import hashlib
import hmac

from app.services.whatsapp.message_parser import parse_messages, parse_statuses
from app.webhooks.meta_whatsapp import _verify_signature

APP_SECRET = "test-app-secret"


def _sign(body: bytes) -> str:
    return "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()


def test_valid_signature_passes() -> None:
    body = b'{"hello":"world"}'
    assert _verify_signature(body, _sign(body)) is True


def test_invalid_signature_fails() -> None:
    body = b'{"hello":"world"}'
    assert _verify_signature(body, "sha256=deadbeef") is False


def test_missing_signature_fails() -> None:
    assert _verify_signature(b"{}", None) is False


def test_parse_text_message() -> None:
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [
                                {"wa_id": "51999888777", "profile": {"name": "Juan"}}
                            ],
                            "messages": [
                                {
                                    "id": "wamid.ABC",
                                    "from": "51999888777",
                                    "type": "text",
                                    "text": {"body": "Hola, ¿tienen citas?"},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }
    messages = parse_messages(payload)
    assert len(messages) == 1
    msg = messages[0]
    assert msg.wa_message_id == "wamid.ABC"
    assert msg.wa_id == "51999888777"
    assert msg.contact_name == "Juan"
    assert msg.message_type == "text"
    assert "citas" in msg.text


def test_parse_audio_message_has_media_id() -> None:
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.AUDIO",
                                    "from": "51900000000",
                                    "type": "audio",
                                    "audio": {"id": "media-123"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    messages = parse_messages(payload)
    assert messages[0].message_type == "audio"
    assert messages[0].media_id == "media-123"


def test_parse_statuses() -> None:
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [
                                {"id": "wamid.X", "status": "read", "timestamp": "123"}
                            ]
                        }
                    }
                ]
            }
        ]
    }
    statuses = parse_statuses(payload)
    assert statuses[0].status == "read"
    assert statuses[0].wa_message_id == "wamid.X"
