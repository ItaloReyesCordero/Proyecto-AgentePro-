"""Cobertura del flujo entrante de WhatsApp (services/whatsapp/webhook_handler).

Se usa la BD real (sqlite) vía el fixture ``client`` + AsyncSessionLocal, con el
agente de IA y el cliente de envío mockeados (sin red). Cubre todas las ramas:
duplicado, sin agent_config, audio, "pasar con el dueño", bot inactivo, negocio
bloqueado, respuesta normal, escalado y sincronización con HubSpot.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.agent_config import AgentConfig
from app.models.conversation import Conversation, ConversationAssigneeType, ConversationStatus
from app.models.message import Message, MessageDirection
from app.models.tenant import Tenant
from app.schemas.webhook_meta import ParsedWhatsAppMessage
from app.services.whatsapp import webhook_handler
from tests.helpers import register_and_auth, tenant_id_of


class _Resp:
    """Respuesta falsa del agente IA con los atributos que usa el handler."""

    def __init__(self, **kw):
        self.text = kw.get("text", "Respuesta IA")
        self.tokens_used = kw.get("tokens_used", 12)
        self.lead_score = kw.get("lead_score", 50)
        self.lead_stage = kw.get("lead_stage", "warm")
        self.intent = kw.get("intent", "general")
        self.appointment_date = kw.get("appointment_date")
        self.key_info = kw.get("key_info", {})
        self.should_escalate = kw.get("should_escalate", False)


class _FakeClient:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []
        self.read: list[str] = []

    async def mark_as_read(self, wa_id):
        self.read.append(wa_id)

    async def send_typing_indicator(self, wa_id):
        pass

    async def send_text(self, *, to, text):
        self.sent.append((to, text))


def _patch_agent(monkeypatch, resp: _Resp | None = None):
    class _Agent:
        async def process_whatsapp_message(self, **kw):
            return resp or _Resp()

    monkeypatch.setattr(webhook_handler, "_agent", _Agent())


def _parsed(**kw) -> ParsedWhatsAppMessage:
    return ParsedWhatsAppMessage(
        wa_message_id=kw.get("wa_message_id", "wamid." + uuid.uuid4().hex),
        from_number=kw.get("from_number", "+51999111222"),
        wa_id=kw.get("wa_id", "51999111222"),
        contact_name=kw.get("contact_name", "Cliente"),
        message_type=kw.get("message_type", "text"),
        text=kw.get("text", "Hola"),
    )


async def _load_tenant(db, tid: str) -> Tenant:
    return await db.get(Tenant, uuid.UUID(tid))


async def _messages(tid: str) -> list[Message]:
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Message).where(Message.tenant_id == uuid.UUID(tid)))
        return list(res.scalars().all())


async def _update_config(tid: str, **fields) -> None:
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(AgentConfig).where(AgentConfig.tenant_id == uuid.UUID(tid)))
        cfg = res.scalar_one()
        for k, v in fields.items():
            setattr(cfg, k, v)
        await db.commit()


# --------------------------------------------------------------------------- #


async def test_normal_text_flow(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-normal@example.com")
    tid = await tenant_id_of(body)
    _patch_agent(monkeypatch, _Resp(text="¡Hola! ¿Te ayudo?", lead_score=80, lead_stage="hot"))
    fake = _FakeClient()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(
            db, tenant, _parsed(text="Quiero info"), client_override=fake
        )
        await db.commit()

    assert ("+51999111222", "¡Hola! ¿Te ayudo?") in fake.sent
    msgs = await _messages(tid)
    assert any(m.direction == MessageDirection.INBOUND and m.content == "Quiero info" for m in msgs)
    assert any(m.direction == MessageDirection.OUTBOUND and m.content == "¡Hola! ¿Te ayudo?" for m in msgs)


async def test_duplicate_message_ignored(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-dup@example.com")
    tid = await tenant_id_of(body)
    _patch_agent(monkeypatch)
    fake = _FakeClient()
    wa_id = "wamid.DUP123"

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(
            db, tenant, _parsed(wa_message_id=wa_id), client_override=fake
        )
        await db.commit()
    first_count = len(await _messages(tid))

    # Reenvío del MISMO wa_message_id: se ignora (no agrega mensajes).
    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(
            db, tenant, _parsed(wa_message_id=wa_id), client_override=fake
        )
        await db.commit()
    assert len(await _messages(tid)) == first_count


async def test_missing_agent_config_returns(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-nocfg@example.com")
    tid = await tenant_id_of(body)
    _patch_agent(monkeypatch)
    fake = _FakeClient()

    # Borra el agent_config para forzar el early-return.
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(AgentConfig).where(AgentConfig.tenant_id == uuid.UUID(tid)))
        await db.delete(res.scalar_one())
        await db.commit()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(db, tenant, _parsed(), client_override=fake)
        await db.commit()
    assert fake.sent == []


async def test_audio_message_unsupported_reply(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-audio@example.com")
    tid = await tenant_id_of(body)
    _patch_agent(monkeypatch)
    fake = _FakeClient()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(
            db, tenant, _parsed(message_type="audio", text=""), client_override=fake
        )
        await db.commit()

    assert len(fake.sent) == 1
    assert "nota" in fake.sent[0][1].lower() or "voz" in fake.sent[0][1].lower()


async def test_owner_handoff(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-owner@example.com")
    tid = await tenant_id_of(body)
    await _update_config(tid, owner_contacts=["+51999111222"], escalation_email="due@x.com")
    _patch_agent(monkeypatch)
    fake = _FakeClient()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(
            db, tenant, _parsed(from_number="+51999111222"), client_override=fake
        )
        await db.commit()

    assert len(fake.sent) == 1  # mensaje de derivación, sin pasar por la IA
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Conversation).where(Conversation.tenant_id == uuid.UUID(tid)))
        conv = res.scalars().first()
    assert conv.status == ConversationStatus.ESCALATED


async def test_bot_inactive_after_takeover(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-takeover@example.com")
    tid = await tenant_id_of(body)
    _patch_agent(monkeypatch)
    fake1 = _FakeClient()

    # 1ra interacción: el bot responde y se crea la conversación.
    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(db, tenant, _parsed(), client_override=fake1)
        await db.commit()
    assert fake1.sent

    # El humano toma el control de la conversación.
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Conversation).where(Conversation.tenant_id == uuid.UUID(tid)))
        conv = res.scalars().first()
        conv.assignee_type = ConversationAssigneeType.HUMAN
        conv.status = ConversationStatus.IN_PROGRESS
        await db.commit()

    # 2da interacción: el bot NO responde (conversación tomada por humano).
    fake2 = _FakeClient()
    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(db, tenant, _parsed(), client_override=fake2)
        await db.commit()
    assert fake2.sent == []


async def test_tenant_blocked_no_reply(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-blocked@example.com")
    tid = await tenant_id_of(body)
    _patch_agent(monkeypatch)
    fake = _FakeClient()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        tenant.is_active = False
        await webhook_handler.handle_inbound_message(db, tenant, _parsed(), client_override=fake)
        await db.commit()
    assert fake.sent == []


async def test_escalation_flow(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-esc@example.com")
    tid = await tenant_id_of(body)
    await _update_config(tid, escalation_email="due@x.com")
    _patch_agent(monkeypatch, _Resp(should_escalate=True))
    fake = _FakeClient()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(db, tenant, _parsed(), client_override=fake)
        await db.commit()

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Conversation).where(Conversation.tenant_id == uuid.UUID(tid)))
        conv = res.scalars().first()
    assert conv.status == ConversationStatus.ESCALATED


async def test_hubspot_sync_branch(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="wh-hs@example.com")
    tid = await tenant_id_of(body)
    await _update_config(tid, auto_create_hubspot_contacts=True, auto_create_hubspot_deals=True)
    _patch_agent(monkeypatch, _Resp(lead_score=85, lead_stage="hot"))

    calls: dict[str, object] = {}

    async def _fake_sync(db, contact, tid_):
        calls["synced"] = True
        return "hs-123"

    async def _fake_deal(hubspot_id, name):
        calls["deal"] = (hubspot_id, name)

    monkeypatch.setattr(webhook_handler, "sync_contact_to_hubspot", _fake_sync)
    monkeypatch.setattr(webhook_handler, "create_deal_for_hot_lead", _fake_deal)
    fake = _FakeClient()

    async with AsyncSessionLocal() as db:
        tenant = await _load_tenant(db, tid)
        await webhook_handler.handle_inbound_message(db, tenant, _parsed(), client_override=fake)
        await db.commit()

    assert calls.get("synced") is True
    assert calls.get("deal") == ("hs-123", "Negocio Test")
