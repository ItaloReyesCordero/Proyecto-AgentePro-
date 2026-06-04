"""Tests de integración adicionales del flujo de autenticación."""
from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import API, bearer, register, register_and_auth


async def test_register_creates_owner_role(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    assert body["user"]["role"] == "owner"
    assert body["user"]["tenant_id"]
    assert body["refresh_token"]


async def test_register_duplicate_email_409(client: AsyncClient):
    await register(client, email="dupe@example.com")
    r = await register(client, email="dupe@example.com", business="Otro")
    assert r.status_code == 409


async def test_register_invalid_email_422(client: AsyncClient):
    r = await client.post(
        f"{API}/auth/register",
        json={
            "email": "no-es-correo",
            "password": "Secret123",
            "full_name": "X",
            "business_name": "Y",
        },
    )
    assert r.status_code == 422


async def test_register_unknown_business_type_falls_back(client: AsyncClient):
    r = await register(client, email="bt@example.com", business_type="tipo-inexistente")
    assert r.status_code == 201  # cae a OTHER sin romper


async def test_login_unknown_email_401(client: AsyncClient):
    r = await client.post(f"{API}/auth/login", json={"email": "ghost@example.com", "password": "x"})
    assert r.status_code == 401


async def test_me_returns_current_user(client: AsyncClient):
    _, headers, body = await register_and_auth(client, email="me@example.com")
    r = await client.get(f"{API}/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"


async def test_me_without_token_401(client: AsyncClient):
    r = await client.get(f"{API}/auth/me")
    assert r.status_code == 401


async def test_logout_ok(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.post(f"{API}/auth/logout", headers=headers)
    assert r.status_code == 200


async def test_refresh_returns_new_access_token(client: AsyncClient):
    _, _, body = await register_and_auth(client)
    r = await client.post(f"{API}/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert r.status_code == 200
    assert r.json()["access_token"]


async def test_refresh_with_access_token_rejected(client: AsyncClient):
    token, _, _ = await register_and_auth(client)
    # Un access token no sirve como refresh.
    r = await client.post(f"{API}/auth/refresh", json={"refresh_token": token})
    assert r.status_code == 401


async def test_change_password_flow(client: AsyncClient):
    _, headers, _ = await register_and_auth(client, email="cp@example.com", password="OldPass1")
    r = await client.post(
        f"{API}/auth/change-password",
        json={"current_password": "OldPass1", "new_password": "NewPass2"},
        headers=headers,
    )
    assert r.status_code == 200
    # La nueva entra, la vieja no.
    assert (await client.post(f"{API}/auth/login", json={"email": "cp@example.com", "password": "NewPass2"})).status_code == 200
    assert (await client.post(f"{API}/auth/login", json={"email": "cp@example.com", "password": "OldPass1"})).status_code == 401


async def test_change_password_wrong_current_400(client: AsyncClient):
    _, headers, _ = await register_and_auth(client)
    r = await client.post(
        f"{API}/auth/change-password",
        json={"current_password": "incorrecta", "new_password": "Whatever9"},
        headers=headers,
    )
    assert r.status_code == 400


async def test_change_password_too_short_422(client: AsyncClient):
    _, headers, _ = await register_and_auth(client, password="OldPass1")
    r = await client.post(
        f"{API}/auth/change-password",
        json={"current_password": "OldPass1", "new_password": "123"},
        headers=headers,
    )
    assert r.status_code == 422


async def test_login_with_bad_token_header_401(client: AsyncClient):
    r = await client.get(f"{API}/auth/me", headers=bearer("token-falso"))
    assert r.status_code == 401


async def test_register_missing_fields_422(client: AsyncClient):
    r = await client.post(f"{API}/auth/register", json={"email": "a@example.com"})
    assert r.status_code == 422
