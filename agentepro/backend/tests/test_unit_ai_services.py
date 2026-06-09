"""Tests de las clases-servicio de IA (agent, call_summarizer, instagram,
voice_agent y context_manager con BD), con el cliente Anthropic mockeado.

Se reemplaza ``service.client.messages.create`` por un fake async para no salir
a la red. Se cubren tanto la ruta feliz como las de error/fallback.
"""
from __future__ import annotations

import uuid

import pytest

from app.models.agent_config import AgentConfig
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.tenant import PlanType, Tenant
from app.services.ai.agent import AIAgentService
from app.services.ai.call_summarizer import CallSummarizerService
from app.services.ai.context_manager import get_conversation_context
from app.services.ai.instagram_content_generator import InstagramContentGenerator
from app.services.ai.voice_agent import VoiceAgentService


class _Usage:
    input_tokens = 10
    output_tokens = 5


class _Block:
    def __init__(self, text: str):
        self.text = text


class _Resp:
    def __init__(self, text: str):
        self.content = [_Block(text)]
        self.usage = _Usage()


def _fake_create(text: str):
    async def create(**kwargs):
        return _Resp(text)

    return create


def _boom_create(exc=RuntimeError("api down")):
    async def create(**kwargs):
        raise exc

    return create


def _agent_config() -> AgentConfig:
    return AgentConfig(
        tenant_id=None,
        agent_name="María",
        faqs=[{"question": "¿Horario?", "answer": "9-6"}],
        services=[{"name": "Consulta", "description": "30 min", "price": 80.0}],
    )


# ----------------------------- AIAgentService -----------------------------

async def test_process_whatsapp_message_success(monkeypatch):
    svc = AIAgentService()
    raw = (
        "Claro!<!--ACTION:ESCALATE-->"
        '<!--META:{"intent":"appointment","confidence":0.9,"lead_score":80,'
        '"lead_stage":"hot","actions":["ESCALATE"],"appointment_date":"2026-01-01",'
        '"key_info_extracted":{"name":"Ana"}}-->'
    )
    monkeypatch.setattr(svc.client.messages, "create", _fake_create(raw))

    tenant = Tenant(name="N", plan=PlanType.ENTERPRISE, messages_used_this_month=0)
    conv = Conversation(tenant_id=uuid.uuid4(), contact_id=uuid.uuid4())
    conv.id = uuid.uuid4()

    class _FakeDB:
        async def execute(self, *a, **k):
            class _R:
                def scalars(self_inner):
                    class _S:
                        def all(self_inner2):
                            return []

                    return _S()

            return _R()

    resp = await svc.process_whatsapp_message(
        "Hola", "text", conv, tenant, _agent_config(), _FakeDB()
    )
    assert resp.intent == "appointment"
    assert resp.should_escalate is True
    assert resp.lead_score == 80
    assert tenant.messages_used_this_month == 1


@pytest.mark.parametrize("mtype", ["audio", "image", "document", "sticker"])
async def test_process_whatsapp_message_types(monkeypatch, mtype):
    svc = AIAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Ok"))

    tenant = Tenant(name="N", plan=PlanType.ENTERPRISE, messages_used_this_month=0)
    conv = Conversation(tenant_id=uuid.uuid4(), contact_id=uuid.uuid4())
    conv.id = uuid.uuid4()

    class _FakeDB:
        async def execute(self, *a, **k):
            class _R:
                def scalars(self_inner):
                    class _S:
                        def all(self_inner2):
                            return []

                    return _S()

            return _R()

    resp = await svc.process_whatsapp_message(
        "x", mtype, conv, tenant, _agent_config(), _FakeDB()
    )
    assert resp.text == "Ok"


async def test_process_whatsapp_message_api_error(monkeypatch):
    svc = AIAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _boom_create())

    tenant = Tenant(name="N", plan=PlanType.ENTERPRISE, messages_used_this_month=0)
    conv = Conversation(tenant_id=uuid.uuid4(), contact_id=uuid.uuid4())
    conv.id = uuid.uuid4()

    class _FakeDB:
        async def execute(self, *a, **k):
            class _R:
                def scalars(self_inner):
                    class _S:
                        def all(self_inner2):
                            return []

                    return _S()

            return _R()

    resp = await svc.process_whatsapp_message(
        "Hola", "text", conv, tenant, _agent_config(), _FakeDB()
    )
    assert resp.intent == "error"
    assert "problema técnico" in resp.text


async def test_process_whatsapp_message_plan_limit():
    from app.core.exceptions import PlanLimitExceededError

    svc = AIAgentService()
    tenant = Tenant(name="N", plan=PlanType.TRIAL, messages_used_this_month=10_000_000)
    conv = Conversation(tenant_id=uuid.uuid4(), contact_id=uuid.uuid4())
    conv.id = uuid.uuid4()

    with pytest.raises(PlanLimitExceededError):
        await svc.process_whatsapp_message("Hola", "text", conv, tenant, _agent_config(), None)


async def test_process_instagram_dm(monkeypatch):
    svc = AIAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Hola IG"))

    tenant = Tenant(name="N", plan=PlanType.ENTERPRISE, messages_used_this_month=0)
    conv = Conversation(tenant_id=uuid.uuid4(), contact_id=uuid.uuid4())
    conv.id = uuid.uuid4()

    class _FakeDB:
        async def execute(self, *a, **k):
            class _R:
                def scalars(self_inner):
                    class _S:
                        def all(self_inner2):
                            return []

                    return _S()

            return _R()

    resp = await svc.process_instagram_dm("Hola", conv, tenant, _agent_config(), _FakeDB())
    assert resp.text == "Hola IG"


async def test_test_message_success_and_error(monkeypatch):
    svc = AIAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Respuesta ESCALATE"))
    resp = await svc.test_message("Hola", _agent_config())
    assert resp.should_escalate is True

    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    resp2 = await svc.test_message("Hola", _agent_config())
    assert resp2.intent == "error"


async def test_generate_quick_reply_success_and_error(monkeypatch):
    svc = AIAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Rápida"))
    assert await svc.generate_quick_reply("ctx", _agent_config()) == "Rápida"

    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    out = await svc.generate_quick_reply("ctx", _agent_config())
    assert "Gracias" in out


def test_parse_meta_invalid_json():
    svc = AIAgentService()
    meta = svc._parse_meta("texto <!--META:{no es json}-->")
    assert meta["intent"] == "unknown"


# ----------------------------- CallSummarizerService -----------------------------

async def test_summarize_empty_transcript():
    svc = CallSummarizerService()
    out = await svc.summarize("   ")
    assert out.summary.startswith("Llamada sin transcripción")


async def test_summarize_success(monkeypatch):
    svc = CallSummarizerService()
    payload = (
        '{"summary":"S","key_points":["a"],"sentiment":"positive","intent":"appointment",'
        '"next_action":"NA","appointment_requested":true,"appointment_details":"mañana",'
        '"lead_score":70,"lead_stage":"hot","contact_info_extracted":{"name":"x"}}'
    )
    monkeypatch.setattr(svc.client.messages, "create", _fake_create(payload))
    out = await svc.summarize("Transcripción", call_duration_seconds=125, agent_name="Bot")
    assert out.sentiment == "positive"
    assert out.appointment_requested is True
    assert out.lead_score == 70


async def test_summarize_bad_json(monkeypatch):
    svc = CallSummarizerService()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("no json"))
    out = await svc.summarize("Transcripción")
    assert "Error al parsear" in out.summary


async def test_summarize_api_error(monkeypatch):
    svc = CallSummarizerService()
    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    out = await svc.summarize("Transcripción")
    assert "No se pudo generar" in out.summary


async def test_generate_followup_message_success_and_error(monkeypatch):
    from app.services.ai.call_summarizer import CallSummary

    svc = CallSummarizerService()
    summary = CallSummary(
        summary="s", key_points=["a", "b"], sentiment="neutral", intent="x",
        next_action="seguir", appointment_requested=False, appointment_details=None,
        lead_score=10, lead_stage="cold", contact_info_extracted={}, tokens_used=0,
    )
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Mensaje seguimiento"))
    assert await svc.generate_followup_message(summary, "Ana", "Negocio") == "Mensaje seguimiento"

    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    fallback = await svc.generate_followup_message(summary, "Ana", "Negocio")
    assert "Ana" in fallback


# ----------------------------- InstagramContentGenerator -----------------------------

async def test_generate_post_success_no_image(monkeypatch):
    svc = InstagramContentGenerator()
    payload = (
        '{"caption":"Cap","hashtags":["a"],"image_prompt":"p","cta":"Compra","post_type":"product"}'
    )
    monkeypatch.setattr(svc.client.messages, "create", _fake_create(payload))
    out = await svc.generate_post(
        "tema", "Negocio", "services",
        services=[{"name": "x", "description": "d", "price": 10}],
        generate_image=False,
    )
    assert out.caption == "Cap"
    assert out.post_type == "product"


async def test_generate_post_bad_json_fallback(monkeypatch):
    svc = InstagramContentGenerator()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("no json"))
    out = await svc.generate_post("tema", "Negocio", "services", generate_image=False)
    assert "Negocio" in out.caption


async def test_generate_post_claude_error_raises(monkeypatch):
    svc = InstagramContentGenerator()
    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    with pytest.raises(RuntimeError):
        await svc.generate_post("tema", "Negocio", "services", generate_image=False)


async def test_generate_post_with_image(monkeypatch):
    svc = InstagramContentGenerator()
    payload = '{"caption":"Cap","hashtags":[],"image_prompt":"p","cta":"c","post_type":"product"}'
    monkeypatch.setattr(svc.client.messages, "create", _fake_create(payload))
    monkeypatch.setattr(svc, "_generate_image", lambda prompt: _coro("http://img"))
    from app.config import settings

    monkeypatch.setattr(settings, "FAL_KEY", "fake-key")
    out = await svc.generate_post("tema", "Negocio", "services", generate_image=True)
    assert out.image_url == "http://img"


async def test_generate_image_no_prompt():
    svc = InstagramContentGenerator()
    assert await svc._generate_image("") is None


async def test_generate_image_http_success(monkeypatch):
    import httpx

    svc = InstagramContentGenerator()

    class _FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"images": [{"url": "http://img.png"}]}

    class _FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            return _FakeResp()

    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    out = await svc._generate_image("a prompt")
    assert out == "http://img.png"


async def test_generate_image_http_error(monkeypatch):
    import httpx

    svc = InstagramContentGenerator()

    class _FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            raise RuntimeError("boom")

    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    assert await svc._generate_image("a prompt") is None


async def test_generate_story_caption_success_and_error(monkeypatch):
    svc = InstagramContentGenerator()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Story!"))
    assert await svc.generate_story_caption("post", "Negocio") == "Story!"

    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    out = await svc.generate_story_caption("post", "Negocio")
    assert "Negocio" in out


async def _coro(value):
    return value


# ----------------------------- VoiceAgentService -----------------------------

class _VoiceCfg:
    agent_name = "Lucía"
    language = "es"
    outbound_calling_hours = {}
    welcome_message = None
    max_call_duration_seconds = None
    escalation_phone = None


async def test_voice_agent_generate_response_success(monkeypatch):
    svc = VoiceAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _fake_create("Hola por voz"))
    out = await svc.generate_response("Hola", [], _VoiceCfg(), _agent_config())
    assert "Hola por voz" in out


async def test_voice_agent_generate_response_error(monkeypatch):
    svc = VoiceAgentService()
    monkeypatch.setattr(svc.client.messages, "create", _boom_create())
    out = await svc.generate_response("Hola", [], _VoiceCfg(), _agent_config())
    assert "no le escuché" in out


# ----------------------------- context_manager (BD) -----------------------------

async def test_get_conversation_context_with_db(client):
    """Usa la BD real (sqlite) para cubrir get_conversation_context."""
    from app.database import AsyncSessionLocal
    from tests.helpers import register_and_auth, seed_contact, seed_conversation, tenant_id_of

    _t, _h, body = await register_and_auth(client, email="ctx@example.com")
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)

    async with AsyncSessionLocal() as db:
        db.add(Message(
            tenant_id=uuid.UUID(tid), conversation_id=uuid.UUID(conv_id),
            direction="inbound", content="Hola",
            message_type="text",
        ))
        db.add(Message(
            tenant_id=uuid.UUID(tid), conversation_id=uuid.UUID(conv_id),
            direction="outbound", content="",
            transcription="Respuesta", message_type="text",
        ))
        # mensaje vacío que debe ser ignorado
        db.add(Message(
            tenant_id=uuid.UUID(tid), conversation_id=uuid.UUID(conv_id),
            direction="inbound", content="",
            message_type="text",
        ))
        await db.commit()

    async with AsyncSessionLocal() as db:
        ctx = await get_conversation_context(uuid.UUID(conv_id), db)
    assert {"role": "user", "content": "Hola"} in ctx
    assert any(m["role"] == "assistant" for m in ctx)


async def test_get_conversation_context_char_limit(client):
    from app.database import AsyncSessionLocal
    from tests.helpers import register_and_auth, seed_contact, seed_conversation, tenant_id_of

    _t, _h, body = await register_and_auth(client, email="ctx2@example.com")
    tid = await tenant_id_of(body)
    cid = await seed_contact(tid)
    conv_id = await seed_conversation(tid, cid)

    async with AsyncSessionLocal() as db:
        for _ in range(5):
            db.add(Message(
                tenant_id=uuid.UUID(tid), conversation_id=uuid.UUID(conv_id),
                direction="inbound", content="x" * 400,
                message_type="text",
            ))
        await db.commit()

    async with AsyncSessionLocal() as db:
        ctx = await get_conversation_context(uuid.UUID(conv_id), db, max_chars=500)
    # con límite de 500 chars y mensajes de ~400 (truncados a 500), solo cabe 1
    assert len(ctx) <= 2
