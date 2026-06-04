"""Tests de integración del cobro manual (Yape/transferencia, sin pasarela).

Cubren el caso real del dueño: un negocio en prueba a punto de vencer aparece
en 'Cobros por revisar', se le confirma el pago (Yape) y se reactiva; si no paga
se le suspende y el panel se bloquea con 402 PAYMENT_OVERDUE.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from httpx import AsyncClient

from tests.conftest import ADMIN_HEADERS
from tests.helpers import API, bearer, register_and_auth


async def _set_trial_ends(tenant_id: str, days_from_now: float) -> None:
    """Mueve la fecha de fin de prueba para simular un trial casi vencido."""
    from app.database import AsyncSessionLocal
    from app.models.tenant import Tenant

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tenant_id))
        tenant.trial_ends_at = datetime.now(tz=timezone.utc) + timedelta(days=days_from_now)
        await db.commit()


async def test_trial_about_to_expire_appears_in_pending(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    await _set_trial_ends(tid, days_from_now=1)  # vence mañana

    r = await client.get(f"{API}/admin/billing/pending", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    rows = {row["id"]: row for row in r.json()}
    assert tid in rows
    assert rows[tid]["payment_state"] == "due_soon"


async def test_expired_trial_is_overdue_in_pending(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    await _set_trial_ends(tid, days_from_now=-1)  # ya venció

    rows = (await client.get(f"{API}/admin/billing/pending", headers=ADMIN_HEADERS)).json()
    state = {row["id"]: row["payment_state"] for row in rows}.get(tid)
    assert state == "overdue"


async def test_expired_trial_blocks_dashboard(client: AsyncClient):
    token, headers, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    await _set_trial_ends(tid, days_from_now=-1)

    r = await client.get(f"{API}/tenants/me", headers=headers)
    assert r.status_code == 402
    assert r.json()["code"] == "TRIAL_EXPIRED"


async def test_confirm_payment_reactivates_expired_trial(client: AsyncClient):
    token, headers, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    await _set_trial_ends(tid, days_from_now=-1)

    # Bloqueado por trial vencido.
    assert (await client.get(f"{API}/tenants/me", headers=headers)).status_code == 402

    # El dueño paga por Yape → el fundador confirma → pasa a 'basic' y reactiva.
    r = await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json()["plan"] == "basic"

    # Ya puede entrar.
    assert (await client.get(f"{API}/tenants/me", headers=headers)).status_code == 200


async def test_confirm_payment_accumulates_when_paid_early(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    # Primer pago.
    first = await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    due1 = first.json()["next_payment_due"]
    # Segundo pago anticipado: el vencimiento se acumula (queda más lejos).
    second = await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    due2 = second.json()["next_payment_due"]
    assert due2 > due1


async def test_confirm_payment_custom_plan_and_amount(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    r = await client.post(
        f"{API}/admin/tenants/{tid}/confirm-payment",
        json={"plan": "enterprise", "amount_pen": 549},
        headers=ADMIN_HEADERS,
    )
    assert r.status_code == 200
    assert r.json()["plan"] == "enterprise"
    assert r.json()["monthly_amount_pen"] == 549


async def test_confirm_payment_invalid_plan_422(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    r = await client.post(
        f"{API}/admin/tenants/{tid}/confirm-payment",
        json={"plan": "plan-pirata"},
        headers=ADMIN_HEADERS,
    )
    assert r.status_code == 422


async def test_suspend_blocks_then_confirm_reactivates(client: AsyncClient):
    _, headers, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)

    # Suspender por falta de pago.
    await client.post(f"{API}/admin/tenants/{tid}/suspend-billing", headers=ADMIN_HEADERS)
    blocked = await client.get(f"{API}/tenants/me", headers=headers)
    assert blocked.status_code == 402
    assert blocked.json()["code"] == "PAYMENT_OVERDUE"

    # Confirmar pago levanta la suspensión.
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    assert (await client.get(f"{API}/tenants/me", headers=headers)).status_code == 200


async def test_suspended_tenant_in_pending(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    await client.post(f"{API}/admin/tenants/{tid}/suspend-billing", headers=ADMIN_HEADERS)
    rows = (await client.get(f"{API}/admin/billing/pending", headers=ADMIN_HEADERS)).json()
    assert any(r["id"] == tid and r["payment_state"] == "suspended" for r in rows)


async def test_active_paid_tenant_not_in_pending(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    tid = body["user"]["tenant_id"]
    # Pago al día (vence en ~1 mes) → no debe figurar como pendiente.
    await client.post(f"{API}/admin/tenants/{tid}/confirm-payment", json={}, headers=ADMIN_HEADERS)
    rows = (await client.get(f"{API}/admin/billing/pending", headers=ADMIN_HEADERS)).json()
    assert all(r["id"] != tid for r in rows)


async def test_billing_pending_requires_admin(client: AsyncClient):
    assert (await client.get(f"{API}/admin/billing/pending")).status_code == 403
