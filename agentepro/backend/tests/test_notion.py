"""Tests del módulo Notion (CRM): parseo de filas + endpoints connect/status/sync.

El parseo es unitario y puro. Los endpoints se prueban con la API de Notion
mockeada (monkeypatch sobre ``fetch_catalog``) para no salir a la red.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.notion import notion_client
from tests.helpers import API, register_and_auth


def _title(text: str) -> dict:
    return {"type": "title", "title": [{"plain_text": text}]}


def _rich(text: str) -> dict:
    return {"type": "rich_text", "rich_text": [{"plain_text": text}]}


def _number(value) -> dict:
    return {"type": "number", "number": value}


def _select(name: str) -> dict:
    return {"type": "select", "select": {"name": name}}


# ----------------------------- parseo (unitario) -----------------------------

def test_plain_text_extracts_each_type():
    assert notion_client._plain_text(_title("Corte")) == "Corte"
    assert notion_client._plain_text(_rich("Hola mundo")) == "Hola mundo"
    assert notion_client._plain_text(_number(25)) == "25"  # entero sin .0
    assert notion_client._plain_text(_number(25.5)) == "25.5"
    assert notion_client._plain_text(_select("Barbería")) == "Barbería"
    assert notion_client._plain_text({}) == ""


def test_row_to_service_maps_columns():
    props = {
        "Nombre": _title("Corte de cabello"),
        "Precio": _number(25),
        "Descripción": _rich("Corte clásico a tijera"),
        "Categoría": _select("Cabello"),
    }
    svc = notion_client._row_to_service(props)
    assert svc == {
        "name": "Corte de cabello",
        "description": "Corte clásico a tijera",
        "price": "25",
        "category": "Cabello",
    }


def test_row_to_service_uses_title_when_no_named_column():
    props = {"Servicio": _title("Afeitado"), "Price": _rich("S/15")}
    svc = notion_client._row_to_service(props)
    assert svc is not None
    assert svc["name"] == "Afeitado"
    assert svc["price"] == "S/15"


def test_row_to_service_skips_empty_rows():
    assert notion_client._row_to_service({"Precio": _number(10)}) is None


# --------------------------- endpoints (integración) -------------------------

@pytest.mark.asyncio
async def test_notion_status_disconnected_by_default(client: AsyncClient):
    _t, headers, _b = await register_and_auth(client, email="notion1@example.com")
    r = await client.get(f"{API}/notion/status", headers=headers)
    assert r.status_code == 200
    assert r.json()["connected"] is False


@pytest.mark.asyncio
async def test_notion_connect_success_syncs_catalog(client: AsyncClient, monkeypatch):
    async def fake_fetch(api_key, database_id):
        return [
            {"name": "Corte", "description": "", "price": "25", "category": ""},
            {"name": "Barba", "description": "", "price": "15", "category": ""},
        ]

    monkeypatch.setattr(notion_client, "fetch_catalog", fake_fetch)

    _t, headers, _b = await register_and_auth(client, email="notion2@example.com")
    r = await client.post(
        f"{API}/notion/connect",
        headers=headers,
        json={"api_key": "secret_token", "database_id": "abc123def456"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["synced"] == 2

    st = await client.get(f"{API}/notion/status", headers=headers)
    body = st.json()
    assert body["connected"] is True
    assert body["services_count"] == 2


@pytest.mark.asyncio
async def test_notion_connect_bad_credentials_not_persisted(client: AsyncClient, monkeypatch):
    async def boom(api_key, database_id):
        raise notion_client.NotionError("Token de Notion inválido")

    monkeypatch.setattr(notion_client, "fetch_catalog", boom)

    _t, headers, _b = await register_and_auth(client, email="notion3@example.com")
    r = await client.post(
        f"{API}/notion/connect",
        headers=headers,
        json={"api_key": "bad", "database_id": "x" * 32},
    )
    assert r.status_code == 400
    # No debe quedar conectado tras un fallo de credenciales.
    st = await client.get(f"{API}/notion/status", headers=headers)
    assert st.json()["connected"] is False
