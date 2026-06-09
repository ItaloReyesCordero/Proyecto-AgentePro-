"""Cobertura de la lógica de voz: call_handler (eventos de Retell) y
outbound_caller (validaciones y lanzamiento de llamada saliente).

Se usa la BD real (sqlite) y se mockea el resumidor de IA y el horario, sin red.
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.call import Call, CallDirection, CallStatus
from app.models.contact import Contact
from app.models.tenant import PlanType, Tenant
from app.models.voice_config import VoiceConfig
from app.schemas.webhook_retell import RetellCallEvent
from app.services.voice import call_handler, outbound_caller
from app.services.voice.outbound_caller import OutboundCallError, call_lead
from tests.helpers import register_and_auth, tenant_id_of


class _Summary:
    summary = "Resumen de la llamada"
    key_points = ["punto a"]
    sentiment = "positive"
    intent = "appointment"
    next_action = "mañana 3pm"
    appointment_requested = True
    appointment_details = "mañana 3pm"
    lead_score = 60
    lead_stage = "warm"
    contact_info_extracted = {}
    tokens_used = 5


async def _set_plan(tid: str, plan: PlanType) -> None:
    async with AsyncSessionLocal() as db:
        t = await db.get(Tenant, uuid.UUID(tid))
        t.plan = plan
        await db.commit()


async def _del_voice_config(tid: str) -> None:
    """El registro ya crea un VoiceConfig; lo borra para probar su ausencia."""
    async with AsyncSessionLocal() as db:
        vc = (await db.execute(select(VoiceConfig).where(VoiceConfig.tenant_id == uuid.UUID(tid)))).scalar_one_or_none()
        if vc:
            await db.delete(vc)
            await db.commit()


async def _mk_contact(tid: str, *, opted_in: bool = True, phone: str | None = "+51900111", wa: str = "51900111") -> str:
    async with AsyncSessionLocal() as db:
        c = Contact(
            tenant_id=uuid.UUID(tid), full_name="Lead", wa_id=wa,
            phone_number=phone, opted_in=opted_in,
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        return str(c.id)


# --------------------------- call_handler --------------------------- #


async def test_call_started_then_ended(client):
    _t, _h, body = await register_and_auth(client, email="voice1@example.com")
    tid = await tenant_id_of(body)
    ev = RetellCallEvent(event="call_started", call_id="rc-1", direction="inbound", from_number="+51900")

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        await call_handler.handle_call_started(db, tenant, ev)  # crea
        await call_handler.handle_call_started(db, tenant, ev)  # existente -> IN_PROGRESS
        await db.commit()

    ev_end = RetellCallEvent(event="call_ended", call_id="rc-1", duration_ms=65000, transcript="hola", recording_url="http://rec")
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        await call_handler.handle_call_ended(db, tenant, ev_end)
        await db.commit()

    async with AsyncSessionLocal() as db:
        call = (await db.execute(select(Call).where(Call.retell_call_id == "rc-1"))).scalar_one()
    assert call.status == CallStatus.COMPLETED
    assert call.duration_seconds == 65


async def test_call_ended_creates_when_missing(client):
    _t, _h, body = await register_and_auth(client, email="voice2@example.com")
    tid = await tenant_id_of(body)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        await call_handler.handle_call_ended(db, tenant, RetellCallEvent(event="call_ended", call_id="rc-x", duration_ms=1000))
        await db.commit()
    async with AsyncSessionLocal() as db:
        call = (await db.execute(select(Call).where(Call.retell_call_id == "rc-x"))).scalar_one()
    assert call.status == CallStatus.COMPLETED


async def test_call_analyzed_full(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="voice3@example.com")
    tid = await tenant_id_of(body)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        await call_handler.handle_call_started(db, tenant, RetellCallEvent(event="call_started", call_id="rc-an", from_number="+51900"))
        await db.commit()

    async def _fake_sum(**kw):
        return _Summary()

    monkeypatch.setattr(call_handler._summarizer, "summarize", _fake_sum)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        await call_handler.handle_call_analyzed(db, tenant, RetellCallEvent(event="call_analyzed", call_id="rc-an", transcript="Cliente quiere cita"))
        await db.commit()

    async with AsyncSessionLocal() as db:
        call = (await db.execute(select(Call).where(Call.retell_call_id == "rc-an"))).scalar_one()
    assert call.sentiment == "positive"


async def test_call_analyzed_missing_and_empty(client):
    _t, _h, body = await register_and_auth(client, email="voice4@example.com")
    tid = await tenant_id_of(body)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        # no existe la llamada -> return temprano
        await call_handler.handle_call_analyzed(db, tenant, RetellCallEvent(event="call_analyzed", call_id="nope"))
        # existe pero sin transcript -> return temprano
        await call_handler.handle_call_started(db, tenant, RetellCallEvent(event="call_started", call_id="rc-e"))
        await call_handler.handle_call_analyzed(db, tenant, RetellCallEvent(event="call_analyzed", call_id="rc-e", transcript="   "))
        await db.commit()


async def test_process_retell_event_dispatch(client):
    _t, _h, body = await register_and_auth(client, email="voice5@example.com")
    tid = await tenant_id_of(body)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        await call_handler.process_retell_event(db, tenant, RetellCallEvent(event="call_started", call_id="rc-d"))
        await call_handler.process_retell_event(db, tenant, RetellCallEvent(event="evento_desconocido", call_id="rc-d"))
        await db.commit()


# --------------------------- outbound_caller --------------------------- #


async def test_call_lead_simulated_success(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="ob-ok@example.com")  # TRIAL incluye voz
    tid = await tenant_id_of(body)
    cid = await _mk_contact(tid)
    monkeypatch.setattr(outbound_caller, "is_within_business_hours", lambda h: True)

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        call = await call_lead(db, tenant, contact)
        await db.commit()
    assert call.direction == CallDirection.OUTBOUND


async def test_call_lead_blocked(client):
    _t, _h, body = await register_and_auth(client, email="ob-block@example.com")
    tid = await tenant_id_of(body)
    cid = await _mk_contact(tid)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        tenant.is_active = False
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_no_voice_feature(client):
    _t, _h, body = await register_and_auth(client, email="ob-nofeat@example.com")
    tid = await tenant_id_of(body)
    await _set_plan(tid, PlanType.INICIAL)  # sin voz
    cid = await _mk_contact(tid)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_limit_reached(client):
    _t, _h, body = await register_and_auth(client, email="ob-limit@example.com")
    tid = await tenant_id_of(body)
    await _set_plan(tid, PlanType.PROFESSIONAL)
    cid = await _mk_contact(tid)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        tenant.calls_used_this_month = 10_000
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_not_opted_in(client):
    _t, _h, body = await register_and_auth(client, email="ob-opt@example.com")
    tid = await tenant_id_of(body)
    cid = await _mk_contact(tid, opted_in=False)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_no_voice_config(client):
    _t, _h, body = await register_and_auth(client, email="ob-nocfg@example.com")
    tid = await tenant_id_of(body)
    await _del_voice_config(tid)
    cid = await _mk_contact(tid)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_outside_hours(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="ob-hours@example.com")
    tid = await tenant_id_of(body)
    cid = await _mk_contact(tid)
    monkeypatch.setattr(outbound_caller, "is_within_business_hours", lambda h: False)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_recent_call(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="ob-recent@example.com")
    tid = await tenant_id_of(body)
    cid = await _mk_contact(tid)
    monkeypatch.setattr(outbound_caller, "is_within_business_hours", lambda h: True)
    async with AsyncSessionLocal() as db:
        db.add(Call(
            tenant_id=uuid.UUID(tid), contact_id=uuid.UUID(cid),
            direction=CallDirection.OUTBOUND, status=CallStatus.COMPLETED,
            from_number="+51", to_number="+51900111",
        ))
        await db.commit()
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)


async def test_call_lead_no_number(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="ob-nonum@example.com")
    tid = await tenant_id_of(body)
    cid = await _mk_contact(tid, phone=None, wa="")
    monkeypatch.setattr(outbound_caller, "is_within_business_hours", lambda h: True)
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        contact = await db.get(Contact, uuid.UUID(cid))
        with pytest.raises(OutboundCallError):
            await call_lead(db, tenant, contact)
