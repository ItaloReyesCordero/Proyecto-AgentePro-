"""Tests de integración de endpoints variados: subscriptions, automations,
instagram, calls y voice."""
from __future__ import annotations

import uuid

from httpx import AsyncClient

from tests.helpers import API, register_and_auth, set_plan


# --- Subscriptions ----------------------------------------------------------


async def test_subscription_me_404_when_none(client: AsyncClient):
    # Un negocio recién registrado no tiene fila de Subscription.
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/subscriptions/me", headers=headers)
    assert r.status_code == 404


async def test_subscription_requires_auth(client: AsyncClient):
    assert (await client.get(f"{API}/subscriptions/me")).status_code == 401


# --- Automations ------------------------------------------------------------


async def test_list_automations_ok(client: AsyncClient):
    # Automatizaciones es módulo solo de Enterprise: el negocio debe estar en ese plan.
    _, headers, body = await register_and_auth(client)
    await set_plan(body["user"]["tenant_id"], "enterprise")
    r = await client.get(f"{API}/automations", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_update_automation_404(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    await set_plan(body["user"]["tenant_id"], "enterprise")
    r = await client.patch(f"{API}/automations/{uuid.uuid4()}", json={"is_active": True}, headers=headers)
    assert r.status_code == 404


async def test_automation_runs_404(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    await set_plan(body["user"]["tenant_id"], "enterprise")
    r = await client.get(f"{API}/automations/{uuid.uuid4()}/runs", headers=headers)
    assert r.status_code == 404


async def test_run_automation_404(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    await set_plan(body["user"]["tenant_id"], "enterprise")
    r = await client.post(f"{API}/automations/{uuid.uuid4()}/run", headers=headers)
    assert r.status_code == 404


async def test_automations_require_auth(client: AsyncClient):
    assert (await client.get(f"{API}/automations")).status_code == 401


async def test_automations_locked_for_non_enterprise(client: AsyncClient):
    # Un plan sin el módulo (p. ej. básico) recibe 402 FEATURE_LOCKED.
    _, headers, body = await register_and_auth(client)
    await set_plan(body["user"]["tenant_id"], "basic")
    r = await client.get(f"{API}/automations", headers=headers)
    assert r.status_code == 402
    assert r.json()["code"] == "FEATURE_LOCKED"


# --- Instagram --------------------------------------------------------------


async def test_list_instagram_posts_empty(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/instagram/posts", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_get_instagram_post_404(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/instagram/posts/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


async def test_instagram_connect_url(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/instagram/connect-url", headers=headers)
    assert r.status_code == 200
    assert "url" in r.json()


async def test_instagram_requires_auth(client: AsyncClient):
    assert (await client.get(f"{API}/instagram/posts")).status_code == 401


# --- Calls ------------------------------------------------------------------


async def test_list_calls_empty(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/calls", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_get_call_404(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/calls/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


async def test_calls_require_auth(client: AsyncClient):
    assert (await client.get(f"{API}/calls")).status_code == 401


# --- Voice ------------------------------------------------------------------


async def test_voice_config_get(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/voice/config", headers=headers)
    assert r.status_code == 200
    assert "voice_id" in r.json()


async def test_voice_config_update(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.put(f"{API}/voice/config", json={"agent_name": "Carla"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["agent_name"] == "Carla"


async def test_voice_requires_auth(client: AsyncClient):
    assert (await client.get(f"{API}/voice/config")).status_code == 401
