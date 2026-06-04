"""Tests de integración del panel del fundador (/admin)."""
from __future__ import annotations

import uuid

from httpx import AsyncClient

from tests.conftest import ADMIN_HEADERS
from tests.helpers import API, register, register_and_auth, tenant_id_of


async def _first_tenant_id(client: AsyncClient) -> str:
    r = await client.get(f"{API}/admin/tenants", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    return r.json()[0]["id"]


# --- Guard ------------------------------------------------------------------


async def test_admin_list_requires_key(client: AsyncClient):
    assert (await client.get(f"{API}/admin/tenants")).status_code == 403


async def test_admin_wrong_key_403(client: AsyncClient):
    r = await client.get(f"{API}/admin/tenants", headers={"X-Admin-Key": "mala"})
    assert r.status_code == 403


async def test_superadmin_bearer_passes_guard(client: AsyncClient):
    # Un superadmin con su JWT normal puede usar el panel.
    from app.core.security import create_access_token, hash_password
    from app.database import AsyncSessionLocal
    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as db:
        u = User(
            email="root2@example.com",
            hashed_password=hash_password("x"),
            full_name="Root",
            role=UserRole.SUPERADMIN,
        )
        db.add(u)
        await db.commit()
        await db.refresh(u)
        token = create_access_token({"sub": str(u.id), "tenant_id": None})
    r = await client.get(f"{API}/admin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


# --- Tenants CRUD -----------------------------------------------------------


async def test_list_tenants(client: AsyncClient):
    await register(client)
    r = await client.get(f"{API}/admin/tenants", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_get_tenant_by_id(client: AsyncClient):
    await register(client, business="Panadería")
    tid = await _first_tenant_id(client)
    r = await client.get(f"{API}/admin/tenants/{tid}", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json()["name"] == "Panadería"


async def test_get_tenant_404(client: AsyncClient):
    r = await client.get(f"{API}/admin/tenants/{uuid.uuid4()}", headers=ADMIN_HEADERS)
    assert r.status_code == 404


async def test_update_tenant_plan_and_name(client: AsyncClient):
    await register(client)
    tid = await _first_tenant_id(client)
    r = await client.patch(
        f"{API}/admin/tenants/{tid}",
        json={"name": "Renombrado", "plan": "professional"},
        headers=ADMIN_HEADERS,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Renombrado"
    assert r.json()["plan"] == "professional"


async def test_deactivate_tenant(client: AsyncClient):
    await register(client)
    tid = await _first_tenant_id(client)
    r = await client.post(f"{API}/admin/tenants/{tid}/deactivate", headers=ADMIN_HEADERS)
    assert r.status_code == 200


async def test_create_tenant_manual(client: AsyncClient):
    r = await client.post(
        f"{API}/admin/tenants",
        json={
            "business_name": "Manual SAC",
            "business_type": "services",
            "owner_name": "Dueño",
            "owner_email": "manual@example.com",
            "owner_phone": "+51999000111",
            "plan": "basic",
        },
        headers=ADMIN_HEADERS,
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Manual SAC"


async def test_create_tenant_duplicate_email_409(client: AsyncClient):
    await register(client, email="ya@example.com")
    r = await client.post(
        f"{API}/admin/tenants",
        json={
            "business_name": "Otro",
            "owner_name": "X",
            "owner_email": "ya@example.com",
            "owner_phone": "+51999",
        },
        headers=ADMIN_HEADERS,
    )
    assert r.status_code == 409


async def test_delete_tenant(client: AsyncClient):
    await register(client)
    tid = await _first_tenant_id(client)
    r = await client.delete(f"{API}/admin/tenants/{tid}", headers=ADMIN_HEADERS)
    assert r.status_code == 200


async def test_export_tenant(client: AsyncClient):
    await register(client)
    tid = await _first_tenant_id(client)
    r = await client.get(f"{API}/admin/tenants/{tid}/export", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert "tenant" in body and "users" in body
    # Nunca debe exponer secretos.
    assert "hashed_password" not in body["tenant"]
    for u in body["users"]:
        assert "hashed_password" not in u


# --- Métricas globales ------------------------------------------------------


async def test_global_metrics(client: AsyncClient):
    await register(client)
    r = await client.get(f"{API}/admin/metrics/global", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json()["total_tenants"] == 1


async def test_global_costs(client: AsyncClient):
    r = await client.get(f"{API}/admin/costs/global", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert "claude_usd_est" in r.json()


async def test_analytics(client: AsyncClient):
    await register(client)
    r = await client.get(f"{API}/admin/analytics", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert "totals" in body and "by_plan" in body and "tenants" in body


async def test_services_health_shape(client: AsyncClient):
    r = await client.get(f"{API}/admin/health", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    body = r.json()
    for svc in ("anthropic", "meta_whatsapp", "twilio", "retell", "culqi"):
        assert svc in body
        assert isinstance(body[svc], bool)


async def test_reset_usage(client: AsyncClient):
    await register(client)
    r = await client.post(f"{API}/admin/reset-usage", headers=ADMIN_HEADERS)
    assert r.status_code == 200


# --- Recuperación de contraseña (panel) -------------------------------------


async def test_reset_owner_password_then_login(client: AsyncClient):
    await register(client, email="ow@example.com", password="OldOne1")
    tid = await _first_tenant_id(client)
    r = await client.post(f"{API}/admin/tenants/{tid}/reset-owner-password", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    new_pw = r.json()["new_password"]
    assert (await client.post(f"{API}/auth/login", json={"email": "ow@example.com", "password": new_pw})).status_code == 200


async def test_webhook_logs_empty(client: AsyncClient):
    await register(client)
    tid = await _first_tenant_id(client)
    r = await client.get(f"{API}/admin/tenants/{tid}/webhooks", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json() == []
