"""Tests de integración de /tenants (panel del negocio)."""
from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import API, register_and_auth


async def test_payment_info_is_public(client: AsyncClient):
    r = await client.get(f"{API}/tenants/payment-info")
    assert r.status_code == 200
    body = r.json()
    for key in ("yape_number", "account_holder", "bank_account", "contact_whatsapp", "note", "configured"):
        assert key in body


async def test_me_returns_tenant(client: AsyncClient):
    _, headers, _ = await register_and_auth(client, business="Mi Negocio")
    r = await client.get(f"{API}/tenants/me", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Mi Negocio"
    assert body["plan"] == "trial"
    assert body["is_active"] is True


async def test_me_requires_auth(client: AsyncClient):
    r = await client.get(f"{API}/tenants/me")
    assert r.status_code == 401


async def test_me_includes_billing_fields(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    body = (await client.get(f"{API}/tenants/me", headers=headers)).json()
    for key in ("payment_state", "billing_suspended", "trial_ends_at", "messages_used_this_month"):
        assert key in body


async def test_new_tenant_starts_in_trial(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    body = (await client.get(f"{API}/tenants/me", headers=headers)).json()
    assert body["plan"] == "trial"
    assert body["trial_ends_at"] is not None
    assert body["billing_suspended"] is False
