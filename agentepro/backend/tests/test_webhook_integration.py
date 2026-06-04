from __future__ import annotations

import hashlib
import hmac
import json

import pytest
from httpx import AsyncClient

APP_SECRET = "test-app-secret"  # debe coincidir con conftest META_APP_SECRET
WH = "/webhooks"


def _sign(body: bytes) -> str:
    """Firma estilo Meta (X-Hub-Signature-256)."""
    return "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()


async def _seed_tenant(
    slug: str,
    *,
    verify_token: str = "verify-123",
    is_active: bool = True,
    retell_agent_id: str | None = None,
):
    """Inserta un tenant directamente (los webhooks usan AsyncSessionLocal, no DI).

    A propósito NO se crea AgentConfig: así `handle_inbound_message` corta en el
    paso 2 ("agent_config_missing") y el background task no llama a la IA.
    """
    from app.database import AsyncSessionLocal
    from app.models.tenant import BusinessType, PlanType, Tenant

    async with AsyncSessionLocal() as db:
        tenant = Tenant(
            name=f"Negocio {slug}",
            slug=slug,
            business_type=BusinessType.SERVICES,
            plan=PlanType.PROFESSIONAL,
            is_active=is_active,
            webhook_verify_token=verify_token,
            retell_agent_id=retell_agent_id,
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        return tenant.id


# --- WhatsApp: verificación GET (handshake de Meta) -------------------------


async def test_whatsapp_verify_returns_challenge(client: AsyncClient) -> None:
    await _seed_tenant("acme", verify_token="tok-ok")
    r = await client.get(
        f"{WH}/whatsapp/acme",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "tok-ok",
            "hub.challenge": "1234567890",
        },
    )
    assert r.status_code == 200
    assert r.text == "1234567890"


async def test_whatsapp_verify_wrong_token_forbidden(client: AsyncClient) -> None:
    await _seed_tenant("acme", verify_token="tok-ok")
    r = await client.get(
        f"{WH}/whatsapp/acme",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "MAL",
            "hub.challenge": "x",
        },
    )
    assert r.status_code == 403


async def test_whatsapp_verify_unknown_tenant_forbidden(client: AsyncClient) -> None:
    r = await client.get(
        f"{WH}/whatsapp/no-existe",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "lo-que-sea",
            "hub.challenge": "x",
        },
    )
    assert r.status_code == 403


# --- WhatsApp: recepción POST (firma + procesamiento) -----------------------


def _wa_text_payload() -> bytes:
    return json.dumps(
        {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "contacts": [
                                    {"wa_id": "51999000111", "profile": {"name": "Ana"}}
                                ],
                                "messages": [
                                    {
                                        "id": "wamid.INT1",
                                        "from": "51999000111",
                                        "type": "text",
                                        "text": {"body": "Hola"},
                                    }
                                ],
                            }
                        }
                    ]
                }
            ]
        }
    ).encode()


async def test_whatsapp_post_invalid_signature_forbidden(client: AsyncClient) -> None:
    await _seed_tenant("acme")
    body = _wa_text_payload()
    r = await client.post(
        f"{WH}/whatsapp/acme",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=deadbeef", "Content-Type": "application/json"},
    )
    assert r.status_code == 403


async def test_whatsapp_post_missing_signature_forbidden(client: AsyncClient) -> None:
    await _seed_tenant("acme")
    body = _wa_text_payload()
    r = await client.post(
        f"{WH}/whatsapp/acme", content=body, headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 403


async def test_whatsapp_post_valid_signature_accepted(client: AsyncClient) -> None:
    await _seed_tenant("acme")
    body = _wa_text_payload()
    r = await client.post(
        f"{WH}/whatsapp/acme",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body), "Content-Type": "application/json"},
    )
    # Siempre 200 inmediato; el procesamiento corta en "agent_config_missing".
    assert r.status_code == 200


async def test_whatsapp_post_inactive_tenant_still_200(client: AsyncClient) -> None:
    # Firma válida → 200 aunque el tenant esté inactivo (background hace no-op).
    await _seed_tenant("dormido", is_active=False)
    body = _wa_text_payload()
    r = await client.post(
        f"{WH}/whatsapp/dormido",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body), "Content-Type": "application/json"},
    )
    assert r.status_code == 200


# --- Instagram (reusa la misma verificación de firma de Meta) ----------------


async def test_instagram_verify_returns_challenge(client: AsyncClient) -> None:
    await _seed_tenant("foto-shop", verify_token="ig-tok")
    r = await client.get(
        f"{WH}/instagram/foto-shop",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "ig-tok",
            "hub.challenge": "999",
        },
    )
    assert r.status_code == 200
    assert r.text == "999"


async def test_instagram_post_invalid_signature_forbidden(client: AsyncClient) -> None:
    await _seed_tenant("foto-shop")
    body = json.dumps({"entry": []}).encode()
    r = await client.post(
        f"{WH}/instagram/foto-shop",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=bad", "Content-Type": "application/json"},
    )
    assert r.status_code == 403


async def test_instagram_post_valid_signature_accepted(client: AsyncClient) -> None:
    await _seed_tenant("foto-shop")
    body = json.dumps(
        {
            "entry": [
                {
                    "messaging": [
                        {
                            "sender": {"id": "ig-user-1"},
                            "message": {"mid": "mid.1", "text": "Hola IG"},
                        }
                    ]
                }
            ]
        }
    ).encode()
    r = await client.post(
        f"{WH}/instagram/foto-shop",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body), "Content-Type": "application/json"},
    )
    assert r.status_code == 200


# --- Retell (sin RETELL_WEBHOOK_SECRET en test → firma omitida) --------------


async def test_retell_post_accepted_without_secret(client: AsyncClient) -> None:
    await _seed_tenant("voz-co", retell_agent_id="agent_abc")
    body = json.dumps(
        {"event": "call_ended", "call": {"call_id": "c1", "agent_id": "agent_abc"}}
    ).encode()
    r = await client.post(
        f"{WH}/retell/voz-co", content=body, headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 200


async def test_retell_post_unknown_tenant_still_200(client: AsyncClient) -> None:
    body = json.dumps({"event": "call_ended", "call": {"call_id": "c1"}}).encode()
    r = await client.post(
        f"{WH}/retell/fantasma", content=body, headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 200


# --- Twilio voice (devuelve TwiML según estado del tenant) -------------------


async def test_twilio_rejects_tenant_without_agent(client: AsyncClient) -> None:
    await _seed_tenant("sin-agente", retell_agent_id=None)
    r = await client.post(
        f"{WH}/twilio/voice/sin-agente",
        data={"From": "+51900", "To": "+51111", "CallSid": "CA1"},
    )
    assert r.status_code == 200
    assert "no está disponible" in r.text
    assert "<Stream" not in r.text


async def test_twilio_unknown_tenant_rejected(client: AsyncClient) -> None:
    r = await client.post(
        f"{WH}/twilio/voice/fantasma",
        data={"From": "+51900", "To": "+51111", "CallSid": "CA1"},
    )
    assert r.status_code == 200
    assert "no está disponible" in r.text


async def test_twilio_connects_stream_for_provisioned_tenant(client: AsyncClient) -> None:
    await _seed_tenant("listo", retell_agent_id="agent_xyz")
    r = await client.post(
        f"{WH}/twilio/voice/listo",
        data={"From": "+51900", "To": "+51111", "CallSid": "CA2"},
    )
    assert r.status_code == 200
    assert "wss://api.retellai.com/audio-websocket/agent_xyz" in r.text
    assert 'value="listo"' in r.text


# --- Culqi (sin CULQI_WEBHOOK_SECRET en test → firma omitida) ----------------


async def test_culqi_ignored_event_returns_200(client: AsyncClient) -> None:
    body = json.dumps({"type": "ping", "data": {}}).encode()
    r = await client.post(
        f"{WH}/culqi", content=body, headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 200


@pytest.mark.parametrize(
    "event_type,expected_status",
    [
        ("charge.creation.success", "active"),
        ("charge.creation.failed", "past_due"),
        ("subscription.cancelled", "cancelled"),
    ],
)
async def test_culqi_event_updates_subscription(
    client: AsyncClient, event_type: str, expected_status: str
) -> None:
    from app.database import AsyncSessionLocal
    from app.models.subscription import Subscription, SubscriptionStatus

    tenant_id = await _seed_tenant(f"pago-{expected_status}")
    async with AsyncSessionLocal() as db:
        db.add(
            Subscription(
                tenant_id=tenant_id,
                plan="professional",
                status=SubscriptionStatus.TRIALING,
                culqi_subscription_id="sub_test_1",
            )
        )
        await db.commit()

    body = json.dumps(
        {"type": event_type, "data": {"subscription_id": "sub_test_1"}}
    ).encode()
    r = await client.post(
        f"{WH}/culqi", content=body, headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 200

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        sub = (
            await db.execute(
                select(Subscription).where(Subscription.culqi_subscription_id == "sub_test_1")
            )
        ).scalar_one()
        assert sub.status.value == expected_status
