"""Tests de integración del alta self-service (/signup) y provisioning."""
from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import API, register

SIGNUP = f"{API}/signup"


def _payload(**over):
    base = {
        "business_name": "Negocio Signup",
        "business_type": "services",
        "owner_name": "Dueño",
        "owner_email": "signup@example.com",
        "owner_phone": "+51999000111",
        "plan": "basic",
        "password": "Secret123",
    }
    base.update(over)
    return base


async def test_signup_short_password_422(client: AsyncClient):
    r = await client.post(SIGNUP, json=_payload(password="123"))
    assert r.status_code == 422


async def test_signup_missing_password_422(client: AsyncClient):
    payload = _payload()
    payload.pop("password")
    r = await client.post(SIGNUP, json=payload)
    assert r.status_code == 422


async def test_signup_duplicate_email_409(client: AsyncClient):
    await register(client, email="taken@example.com")
    r = await client.post(SIGNUP, json=_payload(owner_email="taken@example.com"))
    assert r.status_code == 409


async def test_signup_invalid_email_422(client: AsyncClient):
    r = await client.post(SIGNUP, json=_payload(owner_email="no-es-correo"))
    assert r.status_code == 422


async def test_signup_happy_path_creates_tenant(client: AsyncClient):
    r = await client.post(SIGNUP, json=_payload())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["access_token"]
    assert "dashboard_url" in body
    # El dueño puede iniciar sesión con su contraseña.
    login = await client.post(
        f"{API}/auth/login", json={"email": "signup@example.com", "password": "Secret123"}
    )
    assert login.status_code == 200
