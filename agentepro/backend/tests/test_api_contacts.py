"""Tests de integración de /contacts (CRM)."""
from __future__ import annotations

import uuid

from httpx import AsyncClient

from tests.helpers import API, register_and_auth, seed_contact, tenant_id_of


async def test_list_contacts_empty(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/contacts", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["page"] == 1


async def test_list_contacts_with_seeded(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    await seed_contact(tid, full_name="Juan Perez", phone_number="+51900000001")
    await seed_contact(tid, full_name="Maria Lopez", phone_number="+51900000002")
    r = await client.get(f"{API}/contacts", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 2


async def test_list_contacts_search_filter(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    await seed_contact(tid, full_name="Juan Perez", phone_number="+51900000001")
    await seed_contact(tid, full_name="Maria Lopez", phone_number="+51900000002")
    r = await client.get(f"{API}/contacts", headers=headers, params={"search": "Juan"})
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["name"] == "Juan Perez"


async def test_get_contact_detail(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid, full_name="Detalle", email="d@example.com")
    r = await client.get(f"{API}/contacts/{cid}", headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Detalle"
    assert r.json()["email"] == "d@example.com"


async def test_get_contact_404(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/contacts/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


async def test_update_contact_name_email(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    r = await client.patch(
        f"{API}/contacts/{cid}",
        json={"name": "Nuevo Nombre", "email": "nuevo@example.com", "notes": "VIP"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Nuevo Nombre"
    assert r.json()["email"] == "nuevo@example.com"
    assert r.json()["notes"] == "VIP"


async def test_update_contact_tags(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    r = await client.patch(f"{API}/contacts/{cid}", json={"tags": ["a", "b"]}, headers=headers)
    assert r.status_code == 200
    assert r.json()["tags"] == ["a", "b"]


async def test_update_contact_lead_stage(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid, qualification_score=0)
    r = await client.patch(f"{API}/contacts/{cid}", json={"lead_stage": "customer"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["lead_stage"] == "customer"


async def test_do_not_contact(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    r = await client.post(f"{API}/contacts/{cid}/do-not-contact", headers=headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


async def test_contact_conversations_empty(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    r = await client.get(f"{API}/contacts/{cid}/conversations", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


async def test_contact_calls_empty(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    r = await client.get(f"{API}/contacts/{cid}/calls", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


async def test_send_whatsapp_without_credentials_returns_failure(client: AsyncClient):
    # Sin credenciales de WhatsApp el envío "falla suave": 200 con success=False.
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid, phone_number="+51999111222")
    r = await client.post(
        f"{API}/contacts/{cid}/send-whatsapp", json={"content": "hola"}, headers=headers
    )
    assert r.status_code == 200
    assert r.json()["success"] is False  # no hay token de WhatsApp aún


async def test_contacts_isolated_between_tenants(client: AsyncClient):
    # El contacto de un negocio no aparece para otro.
    _, headers_a, body_a = await register_and_auth(client, email="a@example.com", business="A")
    tid_a = await tenant_id_of(body_a)
    await seed_contact(tid_a, full_name="Solo de A")

    _, headers_b, _ = await register_and_auth(client, email="b@example.com", business="B")
    r = await client.get(f"{API}/contacts", headers=headers_b)
    assert r.json()["total"] == 0


async def test_list_contacts_pagination(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    for i in range(5):
        await seed_contact(tid, full_name=f"C{i}", phone_number=f"+519000000{i}")
    r = await client.get(f"{API}/contacts", headers=headers, params={"per_page": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["per_page"] == 2
    assert len(body["items"]) == 2
    assert body["pages"] == 3
