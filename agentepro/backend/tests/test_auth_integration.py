from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import ADMIN_HEADERS

API = "/api/v1"


async def _register(
    client: AsyncClient,
    email: str = "owner@example.com",
    password: str = "Secret123",
    business: str = "Negocio Test",
):
    return await client.post(
        f"{API}/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Dueño Test",
            "business_name": business,
            "business_type": "services",
        },
    )


# --- Login ------------------------------------------------------------------


async def test_register_then_login_ok(client: AsyncClient) -> None:
    r = await _register(client)
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["role"] == "owner"
    assert body["access_token"]

    r = await client.post(
        f"{API}/auth/login", json={"email": "owner@example.com", "password": "Secret123"}
    )
    assert r.status_code == 200
    assert r.json()["access_token"]


async def test_login_wrong_password_returns_spanish_error(client: AsyncClient) -> None:
    await _register(client)
    r = await client.post(
        f"{API}/auth/login", json={"email": "owner@example.com", "password": "incorrecta"}
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Correo o contraseña incorrectos"


# --- Recuperación de contraseña (flujo completo) ----------------------------


async def test_password_reset_full_flow(client: AsyncClient) -> None:
    await _register(client, "ana@example.com", "OldPass123")

    # Solicitud para un correo EXISTENTE → mensaje genérico + crea pendiente.
    r_exist = await client.post(
        f"{API}/auth/password-reset-request", json={"email": "ana@example.com"}
    )
    assert r_exist.status_code == 200

    # Solicitud para un correo INEXISTENTE → MISMO mensaje (no filtra existencia).
    r_unknown = await client.post(
        f"{API}/auth/password-reset-request", json={"email": "nadie@example.com"}
    )
    assert r_unknown.status_code == 200
    assert r_exist.json()["message"] == r_unknown.json()["message"]

    # El admin ve EXACTAMENTE una solicitud (la del correo real).
    r = await client.get(f"{API}/admin/password-reset-requests", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    reqs = r.json()
    assert len(reqs) == 1
    assert reqs[0]["email"] == "ana@example.com"
    assert reqs[0]["tenant_name"] == "Negocio Test"

    # Aprobar → contraseña nueva al azar.
    request_id = reqs[0]["id"]
    r = await client.post(
        f"{API}/admin/password-reset-requests/{request_id}/approve", headers=ADMIN_HEADERS
    )
    assert r.status_code == 200
    new_password = r.json()["new_password"]
    assert len(new_password) >= 12

    # La contraseña NUEVA entra; la VIEJA ya no.
    r = await client.post(
        f"{API}/auth/login", json={"email": "ana@example.com", "password": new_password}
    )
    assert r.status_code == 200
    r = await client.post(
        f"{API}/auth/login", json={"email": "ana@example.com", "password": "OldPass123"}
    )
    assert r.status_code == 401

    # La solicitud quedó resuelta (lista vacía).
    r = await client.get(f"{API}/admin/password-reset-requests", headers=ADMIN_HEADERS)
    assert r.json() == []


async def test_reset_request_deduplicates(client: AsyncClient) -> None:
    await _register(client, "dup@example.com", "Pass1234")
    for _ in range(3):
        await client.post(f"{API}/auth/password-reset-request", json={"email": "dup@example.com"})
    r = await client.get(f"{API}/admin/password-reset-requests", headers=ADMIN_HEADERS)
    # Tres solicitudes seguidas no crean tres filas: se reutiliza la pendiente.
    assert len([x for x in r.json() if x["email"] == "dup@example.com"]) == 1


async def test_admin_endpoints_require_auth(client: AsyncClient) -> None:
    r = await client.get(f"{API}/admin/password-reset-requests")
    assert r.status_code == 403


async def test_reset_owner_password_direct(client: AsyncClient) -> None:
    reg = await _register(client, "dir@example.com", "InitPass1")
    tenant_id = reg.json()["user"]["tenant_id"]

    r = await client.post(
        f"{API}/admin/tenants/{tenant_id}/reset-owner-password", headers=ADMIN_HEADERS
    )
    assert r.status_code == 200
    new_password = r.json()["new_password"]

    r = await client.post(
        f"{API}/auth/login", json={"email": "dir@example.com", "password": new_password}
    )
    assert r.status_code == 200


async def test_superadmin_is_not_recoverable(client: AsyncClient) -> None:
    # Un superadmin creado directamente NO debe generar solicitud de recuperación.
    from app.core.security import hash_password
    from app.database import AsyncSessionLocal
    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as db:
        db.add(
            User(
                email="root@example.com",
                hashed_password=hash_password("rootpass"),
                full_name="Root",
                role=UserRole.SUPERADMIN,
            )
        )
        await db.commit()

    r = await client.post(
        f"{API}/auth/password-reset-request", json={"email": "root@example.com"}
    )
    assert r.status_code == 200  # mismo mensaje genérico, sin pistas

    r = await client.get(f"{API}/admin/password-reset-requests", headers=ADMIN_HEADERS)
    assert all(x["email"] != "root@example.com" for x in r.json())
