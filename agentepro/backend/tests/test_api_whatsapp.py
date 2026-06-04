"""Tests de integración de /whatsapp (conexión de la WhatsApp Cloud API)."""
from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import API, register_and_auth


async def test_status_disconnected_by_default(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/whatsapp/status", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["connected"] is False
    assert "/webhooks/whatsapp/" in body["webhook_url"]
    assert body["verify_token"]  # se genera en el registro


async def test_connect_sets_connected(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.post(
        f"{API}/whatsapp/connect",
        json={"phone_number_id": "1234567890", "waba_id": "999", "access_token": "EAAG-token-secreto"},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["connected"] is True
    assert body["phone_number_id"] == "1234567890"


async def test_connect_then_status_reports_connected(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    await client.post(
        f"{API}/whatsapp/connect",
        json={"phone_number_id": "111", "access_token": "tok"},
        headers=headers,
    )
    r = await client.get(f"{API}/whatsapp/status", headers=headers)
    assert r.json()["connected"] is True


async def test_token_is_stored_encrypted(client: AsyncClient):
    # El token jamás se guarda en claro: en la BD debe estar cifrado con Fernet.
    import uuid as _uuid

    from app.database import AsyncSessionLocal
    from app.models.tenant import Tenant
    from app.utils.encryption import decrypt

    _, headers, body = await register_and_auth(client)
    tenant_id = body["user"]["tenant_id"]
    await client.post(
        f"{API}/whatsapp/connect",
        json={"phone_number_id": "111", "access_token": "mi-token-secreto"},
        headers=headers,
    )
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, _uuid.UUID(tenant_id))
        assert tenant.whatsapp_access_token != "mi-token-secreto"
        assert decrypt(tenant.whatsapp_access_token) == "mi-token-secreto"


async def test_disconnect_clears_connection(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    await client.post(
        f"{API}/whatsapp/connect",
        json={"phone_number_id": "111", "access_token": "tok"},
        headers=headers,
    )
    r = await client.post(f"{API}/whatsapp/disconnect", headers=headers)
    assert r.status_code == 200
    assert r.json()["connected"] is False


async def test_connect_requires_fields_422(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.post(f"{API}/whatsapp/connect", json={"waba_id": "x"}, headers=headers)
    assert r.status_code == 422


async def test_whatsapp_requires_auth(client: AsyncClient):
    assert (await client.get(f"{API}/whatsapp/status")).status_code == 401
