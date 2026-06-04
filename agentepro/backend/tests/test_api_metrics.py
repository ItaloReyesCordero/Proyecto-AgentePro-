"""Tests de integración de /metrics (dashboard del negocio)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.helpers import API, register_and_auth, seed_contact, tenant_id_of


async def test_summary_ok(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/metrics/summary", headers=headers)
    assert r.status_code == 200
    body = r.json()
    for key in ("total_messages", "new_leads", "total_calls", "hot_leads_count", "leads_funnel"):
        assert key in body


@pytest.mark.parametrize("period", ["7d", "30d", "90d", "raro"])
async def test_summary_accepts_periods(client: AsyncClient, period):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/metrics/summary", headers=headers, params={"period": period})
    assert r.status_code == 200


async def test_message_volume_returns_series(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/metrics/message-volume", headers=headers, params={"period": "7d"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 7  # un punto por día
    assert {"date", "count"} <= set(data[0].keys())


async def test_message_volume_alias(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/metrics/messages-volume", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_leads_funnel_buckets(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = await tenant_id_of(body)
    await seed_contact(tid, qualification_score=80)  # hot
    await seed_contact(tid, qualification_score=40)  # warm
    await seed_contact(tid, qualification_score=10)  # cold
    r = await client.get(f"{API}/metrics/leads-funnel", headers=headers)
    assert r.status_code == 200
    stages = {p["stage"]: p["count"] for p in r.json()}
    assert stages["hot"] == 1
    assert stages["warm"] == 1
    assert stages["cold"] == 1


async def test_costs_breakdown(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.get(f"{API}/metrics/costs", headers=headers)
    assert r.status_code == 200
    body = r.json()
    for key in ("claude_usd", "twilio_usd", "retell_usd", "total_usd", "tokens_used"):
        assert key in body


async def test_metrics_require_auth(client: AsyncClient):
    assert (await client.get(f"{API}/metrics/summary")).status_code == 401
    assert (await client.get(f"{API}/metrics/costs")).status_code == 401
