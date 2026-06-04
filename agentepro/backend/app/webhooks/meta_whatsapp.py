from __future__ import annotations

import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, Query, Request, Response
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.services.whatsapp.message_parser import parse_messages
from app.services.whatsapp.webhook_handler import handle_inbound_message
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["webhooks"])


def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verifica la firma HMAC-SHA256 de Meta.

    Sin `META_APP_SECRET`: se permite SOLO en desarrollo. En producción se rechaza
    para que nadie pueda inyectar mensajes falsos.
    """
    if not settings.META_APP_SECRET:
        if settings.ENVIRONMENT == "production":
            logger.error("meta_app_secret_missing_in_production")
            return False
        logger.warning("meta_signature_skipped_dev")
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.META_APP_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    received = signature_header.split("=", 1)[1]
    return hmac.compare_digest(expected, received)


@router.get("/whatsapp/{tenant_slug}")
async def verify_whatsapp_webhook(
    tenant_slug: str,
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> Response:
    """Verificación inicial de Meta. Devuelve el challenge en texto plano."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
        tenant = result.scalar_one_or_none()
    if (
        tenant is not None
        and hub_mode == "subscribe"
        and tenant.webhook_verify_token == hub_verify_token
    ):
        return Response(content=hub_challenge, media_type="text/plain", status_code=200)
    return Response(content="Forbidden", status_code=403)


async def _process_payload(tenant_slug: str, payload: dict) -> None:
    """Procesa el payload en background con su propia sesión de DB."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
            tenant = result.scalar_one_or_none()
            if tenant is None or not tenant.is_active:
                return
            for message in parse_messages(payload):
                await handle_inbound_message(db, tenant, message, channel="whatsapp")
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("whatsapp_processing_error", error=str(exc), tenant=tenant_slug)


@router.post("/whatsapp/{tenant_slug}")
async def receive_whatsapp_webhook(
    tenant_slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    """Recibe eventos de WhatsApp. Siempre responde 200 inmediatamente."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not _verify_signature(raw_body, signature):
        logger.warning("whatsapp_invalid_signature", tenant=tenant_slug)
        return Response(status_code=403)

    payload = await request.json()
    background_tasks.add_task(_process_payload, tenant_slug, payload)
    return Response(status_code=200)
