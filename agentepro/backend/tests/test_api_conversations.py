"""Tests de integración de /conversations (bandeja de entrada)."""
from __future__ import annotations

import uuid

from httpx import AsyncClient

from tests.helpers import (
    API,
    register_and_auth,
    seed_contact,
    seed_conversation,
    tenant_id_of,
)


async def test_list_conversations_empty(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/conversations", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_list_conversations_with_seeded(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    await seed_conversation(tid, cid, subject="Hola")
    r = await client.get(f"{API}/conversations", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 1


async def test_get_conversation_detail(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)
    r = await client.get(f"{API}/conversations/{conv_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == conv_id


async def test_get_conversation_404(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/conversations/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


async def test_list_messages_empty(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)
    r = await client.get(f"{API}/conversations/{conv_id}/messages", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_close_conversation(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)
    r = await client.post(f"{API}/conversations/{conv_id}/close", headers=headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


async def test_takeover_then_release(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)
    assert (await client.post(f"{API}/conversations/{conv_id}/takeover", headers=headers)).status_code == 200
    assert (await client.post(f"{API}/conversations/{conv_id}/release", headers=headers)).status_code == 200


async def test_pause_bot(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)
    r = await client.post(f"{API}/conversations/{conv_id}/pause-bot", headers=headers)
    assert r.status_code == 200


async def test_send_manual_message(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid, phone_number="+51999111222")
    conv_id = await seed_conversation(tid, cid)
    r = await client.post(
        f"{API}/conversations/{conv_id}/messages",
        json={"content": "Mensaje manual del dueño"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["content"] == "Mensaje manual del dueño"


async def test_update_conversation_404(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.patch(f"{API}/conversations/{uuid.uuid4()}", json={"notes": "x"}, headers=headers)
    assert r.status_code == 404


async def test_conversations_isolated_between_tenants(client: AsyncClient):
    _, _, body_a = await register_and_auth(client, email="a@example.com", business="A")
    tid_a = await tenant_id_of(body_a)
    cid = await seed_contact(tid_a)
    await seed_conversation(tid_a, cid)
    _, headers_b, _ = await register_and_auth(client, email="b@example.com", business="B")
    r = await client.get(f"{API}/conversations", headers=headers_b)
    assert r.json()["total"] == 0
