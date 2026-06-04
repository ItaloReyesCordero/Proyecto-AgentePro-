"""Tests de la función de citas: parseo de fecha, API CRUD y detección desde el agente."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.services import appointment_service
from tests.helpers import API, register_and_auth, tenant_id_of


# ----------------------------- parse_when (unit) -----------------------------

def test_parse_when_iso_date_only():
    dt, raw = appointment_service.parse_when("2026-06-06")
    assert dt is not None and dt.year == 2026 and dt.month == 6 and dt.day == 6
    assert raw == "2026-06-06"


def test_parse_when_iso_datetime():
    dt, _ = appointment_service.parse_when("2026-06-06T17:30")
    assert dt is not None and dt.hour == 17 and dt.minute == 30


def test_parse_when_natural_text_keeps_raw():
    dt, raw = appointment_service.parse_when("el viernes a las 5")
    assert dt is None
    assert raw == "el viernes a las 5"


def test_parse_when_empty():
    assert appointment_service.parse_when(None) == (None, None)
    assert appointment_service.parse_when("null") == (None, None)


# ------------------------------- API (integración) ---------------------------

@pytest.mark.asyncio
async def test_appointments_empty_by_default(client: AsyncClient):
    _t, headers, _b = await register_and_auth(client, email="appt1@example.com")
    r = await client.get(f"{API}/appointments", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_create_list_update_delete_appointment(client: AsyncClient):
    _t, headers, _b = await register_and_auth(client, email="appt2@example.com")

    # Crear (manual)
    r = await client.post(
        f"{API}/appointments",
        headers=headers,
        json={
            "customer_name": "Juan",
            "customer_phone": "+51999000111",
            "service_name": "Corte",
            "scheduled_at": "2026-06-10T15:00:00+00:00",
        },
    )
    assert r.status_code == 201, r.text
    appt = r.json()
    assert appt["status"] == "confirmed"
    assert appt["service_name"] == "Corte"
    appt_id = appt["id"]

    # Listar
    r = await client.get(f"{API}/appointments", headers=headers)
    assert len(r.json()) == 1

    # Actualizar estado a cancelada
    r = await client.patch(
        f"{API}/appointments/{appt_id}", headers=headers, json={"status": "cancelled"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"

    # Filtrar por estado
    r = await client.get(f"{API}/appointments?status=cancelled", headers=headers)
    assert len(r.json()) == 1
    r = await client.get(f"{API}/appointments?status=confirmed", headers=headers)
    assert r.json() == []

    # Borrar
    r = await client.delete(f"{API}/appointments/{appt_id}", headers=headers)
    assert r.status_code == 204
    r = await client.get(f"{API}/appointments", headers=headers)
    assert r.json() == []


@pytest.mark.asyncio
async def test_appointment_isolated_between_tenants(client: AsyncClient):
    _t, headers_a, _ = await register_and_auth(client, email="ta@example.com", business="A")
    await client.post(
        f"{API}/appointments", headers=headers_a, json={"customer_name": "De A", "service_name": "X"}
    )
    _t, headers_b, _ = await register_and_auth(client, email="tb@example.com", business="B")
    r = await client.get(f"{API}/appointments", headers=headers_b)
    assert r.json() == []


@pytest.mark.asyncio
async def test_maybe_create_from_agent_detects_and_dedupes(client: AsyncClient):
    """La detección crea UNA cita y no duplica en mensajes siguientes."""
    from app.database import AsyncSessionLocal
    from app.models.agent_config import AgentConfig
    from app.models.contact import Contact
    from app.models.tenant import Tenant
    from app.models.appointment import AppointmentSource

    _t, headers, body = await register_and_auth(client, email="appt3@example.com")
    tid = uuid.UUID(await tenant_id_of(body))

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, tid)
        contact = Contact(tenant_id=tid, full_name="Pedro", phone_number="+51988777666", wa_id="51988777666")
        db.add(contact)
        ac = (await db.execute(
            __import__("sqlalchemy").select(AgentConfig).where(AgentConfig.tenant_id == tid)
        )).scalar_one_or_none()
        await db.flush()

        # 1er mensaje: pide cita
        a1 = await appointment_service.maybe_create_from_agent(
            db, tenant=tenant, contact=contact, agent_config=ac,
            intent="appointment", appointment_date="2026-06-12T16:00",
            key_info={"service": "Solo barba"}, source=AppointmentSource.WHATSAPP,
        )
        assert a1 is not None
        assert a1.service_name == "Solo barba"
        assert a1.scheduled_at is not None

        # 2do mensaje en la misma conversación: NO debe crear otra
        a2 = await appointment_service.maybe_create_from_agent(
            db, tenant=tenant, contact=contact, agent_config=ac,
            intent="appointment", appointment_date="2026-06-12T16:00",
            key_info={"service": "Solo barba"}, source=AppointmentSource.WHATSAPP,
        )
        assert a2.id == a1.id  # misma cita (actualiza, no duplica)

        # Sin señal de cita: no crea nada
        a3 = await appointment_service.maybe_create_from_agent(
            db, tenant=tenant, contact=contact, agent_config=ac,
            intent="faq", appointment_date=None, key_info={}, source=AppointmentSource.WHATSAPP,
        )
        # devuelve la cita viva existente (no None) pero no crea otra; basta que no truene
        assert a3 is None or a3.id == a1.id
