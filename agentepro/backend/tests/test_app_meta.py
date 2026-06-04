"""Tests del armazón de la app: arranque, salud, OpenAPI y rutas montadas."""
from __future__ import annotations

from httpx import AsyncClient


def test_app_imports_and_has_routes():
    from app.main import app

    assert len(app.routes) > 80  # ~96 rutas montadas


def test_app_metadata():
    from app.config import settings
    from app.main import app

    assert app.title  # tiene título
    assert settings.VERSION == "2.0.0"


async def test_health_endpoint(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200


async def test_openapi_schema_served(client: AsyncClient):
    r = await client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert schema["info"]["title"]
    assert "paths" in schema


async def test_docs_endpoint_state(client: AsyncClient):
    # Swagger UI puede estar habilitado (dev) o deshabilitado (prod/test, DEBUG=false).
    # Cualquiera de los dos es válido; lo que importa es que el esquema OpenAPI exista.
    r = await client.get("/docs")
    assert r.status_code in (200, 404)


def test_all_v1_routers_mounted():
    from app.main import app

    paths = {getattr(r, "path", "") for r in app.routes}
    expected_prefixes = [
        "/api/v1/auth",
        "/api/v1/tenants",
        "/api/v1/contacts",
        "/api/v1/conversations",
        "/api/v1/calls",
        "/api/v1/instagram",
        "/api/v1/automations",
        "/api/v1/agent",
        "/api/v1/voice",
        "/api/v1/whatsapp",
        "/api/v1/metrics",
        "/api/v1/subscriptions",
        "/api/v1/admin",
    ]
    for prefix in expected_prefixes:
        assert any(p.startswith(prefix) for p in paths), f"falta router {prefix}"


def test_webhook_routes_mounted():
    from app.main import app

    paths = {getattr(r, "path", "") for r in app.routes}
    assert any("/webhooks/whatsapp" in p for p in paths)


def test_exception_handlers_registered():
    from app.core.exceptions import AgentProException
    from app.main import app

    assert AgentProException in app.exception_handlers
