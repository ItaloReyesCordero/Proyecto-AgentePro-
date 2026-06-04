"""Chequeos de PREPARACIÓN ("readiness") contra el servidor REAL.

A diferencia del resto de la suite (que corre sobre SQLite en memoria), estos
tests apuntan al backend en marcha (Docker/producción) y verifican que cada
negocio YA tiene conectada su WhatsApp Cloud API y que las API keys de la
plataforma están puestas.

➡️  FALLAN A PROPÓSITO hasta que configures todo. Cuando cada negocio tenga su
    WhatsApp conectado y las keys cargadas, darán PASSED.

No se ejecutan en el `pytest` normal (quedan fuera por el marcador `readiness`).
Para correrlos contra tu servidor:

    # apuntando al backend local en Docker:
    pytest -m readiness

    # o a producción:
    READINESS_BASE_URL=https://api.tudominio.com \
    READINESS_ADMIN_KEY=tu-admin-secret-key \
    pytest -m readiness

Si el servidor no responde, los tests se SALTAN (no rompen nada).
"""
from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.readiness

BASE_URL = os.environ.get("READINESS_BASE_URL", "http://localhost:8000")
ADMIN_KEY = os.environ.get("READINESS_ADMIN_KEY") or os.environ.get("ADMIN_SECRET_KEY", "")
API = f"{BASE_URL}/api/v1"


def _client() -> httpx.Client:
    return httpx.Client(timeout=10.0, headers={"X-Admin-Key": ADMIN_KEY})


def _get(path: str) -> httpx.Response:
    try:
        with _client() as c:
            resp = c.get(f"{API}{path}")
    except httpx.HTTPError as exc:  # servidor caído / inalcanzable
        pytest.skip(f"Backend no accesible en {BASE_URL}: {exc}")
    if resp.status_code == 403:
        pytest.skip(
            "READINESS_ADMIN_KEY incorrecta o ausente para el servidor real "
            "(define READINESS_ADMIN_KEY con tu ADMIN_SECRET_KEY de producción)."
        )
    return resp


def _tenants() -> list[dict]:
    r = _get("/admin/tenants")
    if r.status_code == 403:
        pytest.skip("READINESS_ADMIN_KEY incorrecta o ausente para el servidor real.")
    assert r.status_code == 200, f"No se pudo listar negocios: {r.status_code}"
    return r.json()


# --- Plataforma: API keys puestas -------------------------------------------


def test_platform_anthropic_key_configured():
    health = _get("/admin/health").json()
    assert health.get("anthropic") is True, (
        "Falta ANTHROPIC_API_KEY: el agente de IA no podrá responder."
    )


def test_platform_whatsapp_app_secret_configured():
    health = _get("/admin/health").json()
    assert health.get("meta_whatsapp") is True, (
        "Falta META_APP_SECRET: los webhooks de WhatsApp no verificarán firma."
    )


# --- Cada negocio conectado a WhatsApp --------------------------------------


def test_there_is_at_least_one_business():
    tenants = _tenants()
    assert len(tenants) >= 1, "Aún no hay ningún negocio creado en el servidor."


def test_every_business_has_whatsapp_connected():
    """Cada negocio debe tener su WhatsApp Cloud API conectada (phone_number_id).

    Falla listando exactamente qué negocios NO están conectados todavía, para
    que sepas a quién le falta configurar WhatsApp.
    """
    tenants = _tenants()
    if not tenants:
        pytest.skip("No hay negocios todavía.")

    no_conectados: list[str] = []
    for t in tenants:
        export = _get(f"/admin/tenants/{t['id']}/export")
        if export.status_code != 200:
            no_conectados.append(f"{t['name']} (no se pudo leer)")
            continue
        tenant_data = export.json().get("tenant", {})
        if not tenant_data.get("phone_number_id"):
            no_conectados.append(t["name"])

    assert not no_conectados, (
        "Negocios SIN WhatsApp conectado: " + ", ".join(no_conectados)
    )


def test_every_active_business_is_provisioned():
    """Los negocios activos deberían estar aprovisionados (is_provisioned)."""
    tenants = _tenants()
    activos = [t for t in tenants if t.get("is_active")]
    if not activos:
        pytest.skip("No hay negocios activos.")
    sin_provisionar = [t["name"] for t in activos if not t.get("is_provisioned")]
    assert not sin_provisionar, (
        "Negocios activos sin aprovisionar: " + ", ".join(sin_provisionar)
    )
