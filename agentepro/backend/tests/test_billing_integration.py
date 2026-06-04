from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import ADMIN_HEADERS

API = "/api/v1"


async def _register(client: AsyncClient, email: str = "biz@example.com"):
    r = await client.post(
        f"{API}/auth/register",
        json={
            "email": email,
            "password": "Secret123",
            "full_name": "Dueño Test",
            "business_name": "Negocio Cobro",
            "business_type": "services",
        },
    )
    assert r.status_code == 201
    body = r.json()
    return body["access_token"], body


async def _tenant_id(client: AsyncClient) -> str:
    r = await client.get(f"{API}/admin/tenants", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    return r.json()[0]["id"]


async def test_payment_info_public(client: AsyncClient) -> None:
    # Endpoint público (sin auth): nunca debe bloquear.
    r = await client.get(f"{API}/tenants/payment-info")
    assert r.status_code == 200
    body = r.json()
    assert "yape_number" in body and "configured" in body


async def test_confirm_payment_moves_off_trial_and_sets_due(client: AsyncClient) -> None:
    token, _ = await _register(client)
    tid = await _tenant_id(client)

    r = await client.post(
        f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS
    )
    assert r.status_code == 200
    body = r.json()
    assert body["plan"] == "basic"  # trial → basic al confirmar el primer pago
    assert body["next_payment_due"] is not None
    assert body["last_payment_at"] is not None
    assert body["billing_suspended"] is False
    assert body["payment_state"] in ("active", "due_soon")


async def test_confirm_payment_with_plan_and_amount(client: AsyncClient) -> None:
    await _register(client)
    tid = await _tenant_id(client)

    r = await client.post(
        f"{API}/admin/tenants/{tid}/confirm-payment",
        json={"plan": "professional", "amount_pen": 349},
        headers=ADMIN_HEADERS,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["plan"] == "professional"
    assert body["monthly_amount_pen"] == 349


async def test_suspend_blocks_dashboard_then_reactivate(client: AsyncClient) -> None:
    token, _ = await _register(client)
    tid = await _tenant_id(client)
    auth = {"Authorization": f"Bearer {token}"}

    # Pasa a plan pagado primero (si no, el trial sigue activo 14 días).
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)

    # Activo: el dueño entra a su panel.
    assert (await client.get(f"{API}/tenants/me", headers=auth)).status_code == 200

    # Suspender por falta de pago → dashboard bloqueado con 402 PAYMENT_OVERDUE.
    r = await client.post(f"{API}/admin/tenants/{tid}/suspend-billing", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json()["billing_suspended"] is True

    blocked = await client.get(f"{API}/tenants/me", headers=auth)
    assert blocked.status_code == 402
    assert blocked.json()["code"] == "PAYMENT_OVERDUE"

    # Confirmar pago reactiva el servicio.
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    assert (await client.get(f"{API}/tenants/me", headers=auth)).status_code == 200


async def test_billing_pending_lists_suspended(client: AsyncClient) -> None:
    await _register(client)
    tid = await _tenant_id(client)
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    await client.post(f"{API}/admin/tenants/{tid}/suspend-billing", headers=ADMIN_HEADERS)

    r = await client.get(f"{API}/admin/billing/pending", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    rows = r.json()
    assert any(row["id"] == tid and row["payment_state"] == "suspended" for row in rows)
