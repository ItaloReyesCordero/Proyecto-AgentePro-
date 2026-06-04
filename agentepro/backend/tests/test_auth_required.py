"""Verifica que TODOS los endpoints del negocio exigen autenticación y que los
de plataforma exigen la clave de administración. Una regresión aquí sería una
fuga de datos entre negocios, así que se cubre endpoint por endpoint."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.helpers import API

# (método, ruta) de endpoints que requieren token de dueño → deben dar 401 sin él.
TENANT_ENDPOINTS = [
    ("get", "/tenants/me"),
    ("get", "/contacts"),
    ("get", "/contacts/00000000-0000-0000-0000-000000000000"),
    ("get", "/conversations"),
    ("get", "/conversations/00000000-0000-0000-0000-000000000000"),
    ("get", "/calls"),
    ("get", "/calls/00000000-0000-0000-0000-000000000000"),
    ("get", "/instagram/posts"),
    ("get", "/instagram/connect-url"),
    ("get", "/automations"),
    ("get", "/agent/config"),
    ("get", "/agent/config/preview"),
    ("get", "/agent/voice"),
    ("get", "/voice/config"),
    ("get", "/metrics/summary"),
    ("get", "/metrics/message-volume"),
    ("get", "/metrics/leads-funnel"),
    ("get", "/metrics/costs"),
    ("get", "/subscriptions/me"),
    ("get", "/whatsapp/status"),
    ("post", "/whatsapp/disconnect"),
    ("post", "/agent/voice/test-call"),
]

# Endpoints de plataforma → 403 sin la clave de admin.
ADMIN_ENDPOINTS = [
    ("get", "/admin/tenants"),
    ("get", "/admin/metrics/global"),
    ("get", "/admin/costs/global"),
    ("get", "/admin/analytics"),
    ("get", "/admin/health"),
    ("get", "/admin/billing/pending"),
    ("get", "/admin/password-reset-requests"),
    ("post", "/admin/reset-usage"),
]


@pytest.mark.parametrize("method,path", TENANT_ENDPOINTS)
async def test_tenant_endpoint_requires_auth(client: AsyncClient, method, path):
    r = await getattr(client, method)(f"{API}{path}")
    assert r.status_code == 401, f"{method.upper()} {path} no exigió auth ({r.status_code})"


@pytest.mark.parametrize("method,path", ADMIN_ENDPOINTS)
async def test_admin_endpoint_requires_key(client: AsyncClient, method, path):
    r = await getattr(client, method)(f"{API}{path}")
    assert r.status_code == 403, f"{method.upper()} {path} no exigió admin ({r.status_code})"


@pytest.mark.parametrize("method,path", TENANT_ENDPOINTS)
async def test_tenant_endpoint_rejects_garbage_token(client: AsyncClient, method, path):
    r = await getattr(client, method)(f"{API}{path}", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401
