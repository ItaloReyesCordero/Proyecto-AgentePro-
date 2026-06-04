from __future__ import annotations

import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, Request, Response
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.schemas.webhook_retell import RetellCallEvent
from app.services.voice.call_handler import process_retell_event
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["webhooks"])


def _verify_retell_signature(raw_body: bytes, signature: str | None) -> bool:
    if not settings.RETELL_WEBHOOK_SECRET:
        return True
    if not signature:
        return False
    expected = hmac.new(
        settings.RETELL_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _parse_event(body: dict) -> RetellCallEvent:
    call = body.get("call", body)
    return RetellCallEvent(
        event=body.get("event", "unknown"),
        call_id=call.get("call_id", ""),
        agent_id=call.get("agent_id"),
        from_number=call.get("from_number"),
        to_number=call.get("to_number"),
        direction=call.get("direction"),
        transcript=call.get("transcript"),
        recording_url=call.get("recording_url"),
        duration_ms=call.get("duration_ms") or call.get("call_length_ms"),
        disconnection_reason=call.get("disconnection_reason"),
        metadata=call.get("metadata", {}),
    )


async def _process(tenant_slug: str, body: dict) -> None:
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
            tenant = result.scalar_one_or_none()
            if tenant is None:
                return
            await process_retell_event(db, tenant, _parse_event(body))
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("retell_processing_error", error=str(exc), tenant=tenant_slug)


@router.post("/retell/{tenant_slug}")
async def retell_webhook(
    tenant_slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    raw_body = await request.body()
    signature = request.headers.get("X-Retell-Signature")
    if not _verify_retell_signature(raw_body, signature):
        return Response(status_code=403)
    body = await request.json()
    background_tasks.add_task(_process, tenant_slug, body)
    return Response(status_code=200)
