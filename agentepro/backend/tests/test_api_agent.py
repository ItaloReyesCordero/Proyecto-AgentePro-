"""Tests de integración de /agent (configuración del asistente IA)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.helpers import API, register_and_auth


async def test_get_config_returns_defaults(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/agent/config", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "agent_name" in body
    assert "business_hours" in body
    assert body["language"] == "es"


async def test_update_config_agent_name(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.put(f"{API}/agent/config", json={"agent_name": "Sofía"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["agent_name"] == "Sofía"


async def test_patch_config_temperature(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.patch(f"{API}/agent/config", json={"temperature": 0.3}, headers=headers)
    assert r.status_code == 200
    assert r.json()["temperature"] == pytest.approx(0.3)


async def test_update_config_persists(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    await client.put(f"{API}/agent/config", json={"welcome_message": "¡Bienvenido!"}, headers=headers)
    r = await client.get(f"{API}/agent/config", headers=headers)
    assert r.json()["welcome_message"] == "¡Bienvenido!"


async def test_update_business_hours(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    hours = {"lunes": {"active": True, "open": "08:00", "close": "20:00"}}
    r = await client.put(f"{API}/agent/config", json={"business_hours": hours}, headers=headers)
    assert r.status_code == 200
    assert r.json()["business_hours"]["lunes"]["open"] == "08:00"


async def test_update_faqs_and_services(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    payload = {
        "faqs": [{"q": "¿Horario?", "a": "9-6"}],
        "services": [{"name": "Corte", "price": 30}],
    }
    r = await client.put(f"{API}/agent/config", json=payload, headers=headers)
    assert r.status_code == 200
    assert len(r.json()["faqs"]) == 1
    assert len(r.json()["services"]) == 1


async def test_preview_prompt(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/agent/config/preview", headers=headers)
    assert r.status_code == 200
    assert "system_prompt" in r.json()
    assert isinstance(r.json()["system_prompt"], str)


async def test_config_test_degrades_without_api_key(client: AsyncClient):
    # Sin ANTHROPIC_API_KEY el endpoint NO revienta: devuelve una respuesta de error controlada.
    _, headers, _ = await register_and_auth(client)
    r = await client.post(f"{API}/agent/config/test", json={"message": "Hola"}, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert "intent" in body
    assert "lead_score" in body


async def test_get_voice_config(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/agent/voice", headers=headers)
    assert r.status_code == 200
    assert "agent_name" in r.json()


async def test_update_voice_config(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.put(f"{API}/agent/voice", json={"agent_name": "Lucía"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["agent_name"] == "Lucía"


async def test_test_call_without_provisioning_400(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.post(f"{API}/agent/voice/test-call", headers=headers)
    assert r.status_code == 400  # no hay agente de voz provisionado


async def test_agent_config_requires_auth(client: AsyncClient):
    assert (await client.get(f"{API}/agent/config")).status_code == 401
