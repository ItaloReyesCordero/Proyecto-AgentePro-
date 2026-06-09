"""Cobertura de whatsapp/sender (selección de cliente y envío) e
instagram/post_generator (generación y guardado de post), sin red.
"""
from __future__ import annotations

import uuid

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.tenant import PlanType, Tenant
from app.services.instagram import post_generator
from app.services.whatsapp import sender
from tests.helpers import register_and_auth, tenant_id_of


def _tenant(**kw) -> Tenant:
    return Tenant(
        name="N", plan=PlanType.TRIAL,
        phone_number_id=kw.get("pnid"),
        whatsapp_access_token=kw.get("token"),
    )


# ------------------------------ sender ------------------------------ #


def test_build_client_no_creds():
    assert sender.build_client_for_tenant(_tenant()) is None


def test_build_client_with_creds(monkeypatch):
    monkeypatch.setattr(sender, "decrypt_if_value", lambda v: "plain-token")
    assert sender.build_client_for_tenant(_tenant(pnid="123", token="enc")) is not None


def test_build_client_decrypt_empty(monkeypatch):
    monkeypatch.setattr(sender, "decrypt_if_value", lambda v: "")
    assert sender.build_client_for_tenant(_tenant(pnid="123", token="enc")) is None


def test_build_outbound_meta_preferred(monkeypatch):
    monkeypatch.setattr(sender, "decrypt_if_value", lambda v: "t")
    assert sender.build_outbound_client(_tenant(pnid="1", token="e")) is not None


def test_build_outbound_twilio_fallback(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", "AC")
    monkeypatch.setattr(settings, "TWILIO_AUTH_TOKEN", "tok")
    monkeypatch.setattr(settings, "TWILIO_WHATSAPP_FROM", "+14155238886")
    assert sender.build_outbound_client(_tenant()) is not None


def test_build_outbound_none(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", "")
    assert sender.build_outbound_client(_tenant()) is None


async def test_send_no_client_debug(monkeypatch):
    monkeypatch.setattr(sender, "build_outbound_client", lambda t: None)
    monkeypatch.setattr(settings, "DEBUG", True)
    assert await sender.send_whatsapp_message(_tenant(), "+51", "hi") is True


async def test_send_no_client_prod(monkeypatch):
    monkeypatch.setattr(sender, "build_outbound_client", lambda t: None)
    monkeypatch.setattr(settings, "DEBUG", False)
    assert await sender.send_whatsapp_message(_tenant(), "+51", "hi") is False


async def test_send_success_and_error(monkeypatch):
    class _Ok:
        async def send_text(self, *, to, text):
            pass

    monkeypatch.setattr(sender, "build_outbound_client", lambda t: _Ok())
    assert await sender.send_whatsapp_message(_tenant(), "+51", "hi") is True

    class _Bad:
        async def send_text(self, *, to, text):
            raise RuntimeError("falló")

    monkeypatch.setattr(sender, "build_outbound_client", lambda t: _Bad())
    assert await sender.send_whatsapp_message(_tenant(), "+51", "hi") is False


# --------------------------- post_generator --------------------------- #


async def test_generate_and_store_post(client, monkeypatch):
    _t, _h, body = await register_and_auth(client, email="post1@example.com")
    tid = await tenant_id_of(body)

    class _Gen:
        caption = "Caption IA"
        image_url = "http://img.png"
        image_prompt = "un prompt"
        hashtags = ["agentepro"]

    async def _fake(**kw):
        return _Gen()

    monkeypatch.setattr(post_generator._generator, "generate_post", _fake)

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tid))
        post = await post_generator.generate_and_store_post(db, tenant, None, "Promo de verano", generate_image=False)
        await db.commit()
    assert post.caption == "Caption IA"
    assert post.ai_generated_image_url == "http://img.png"
