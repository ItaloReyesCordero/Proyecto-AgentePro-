from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Query, Request, Response
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.services.instagram.dm_handler import handle_instagram_dm, parse_instagram_messages
from app.utils.logger import get_logger
from app.webhooks.meta_whatsapp import _verify_signature

logger = get_logger(__name__)

router = APIRouter(tags=["webhooks"])


@router.get("/instagram/{tenant_slug}")
async def verify_instagram_webhook(
    tenant_slug: str,
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> Response:
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


async def _process(tenant_slug: str, payload: dict) -> None:
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
            tenant = result.scalar_one_or_none()
            if tenant is None or not tenant.is_active:
                return
            for message in parse_instagram_messages(payload):
                await handle_instagram_dm(db, tenant, message)
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("instagram_processing_error", error=str(exc), tenant=tenant_slug)


@router.post("/instagram/{tenant_slug}")
async def receive_instagram_webhook(
    tenant_slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not _verify_signature(raw_body, signature):
        return Response(status_code=403)
    payload = await request.json()
    background_tasks.add_task(_process, tenant_slug, payload)
    return Response(status_code=200)
