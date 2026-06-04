from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request, Response
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.tenant import Tenant
from app.services.culqi_service import CulqiService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["webhooks"])


def _verify(raw_body: bytes, signature: str | None) -> bool:
    if not settings.CULQI_WEBHOOK_SECRET:
        return True
    if not signature:
        return False
    expected = hmac.new(
        settings.CULQI_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _apply_action(action: str, event: dict[str, Any]) -> None:
    """Aplica el efecto del evento de Culqi sobre la suscripción/tenant."""
    data = event.get("data", event)
    culqi_sub_id = data.get("subscription_id") or data.get("id")
    if not culqi_sub_id:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Subscription).where(Subscription.culqi_subscription_id == culqi_sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub is None:
            logger.info("culqi_subscription_not_found", culqi_sub_id=culqi_sub_id)
            return
        now = datetime.now(tz=timezone.utc)
        if action == "renew_subscription":
            sub.status = SubscriptionStatus.ACTIVE
            sub.current_period_start = now
            sub.current_period_end = now + timedelta(days=30)
        elif action == "notify_payment_failed":
            sub.status = SubscriptionStatus.PAST_DUE
        elif action == "deactivate_tenant":
            sub.status = SubscriptionStatus.CANCELLED
            tenant = await db.get(Tenant, sub.tenant_id)
            if tenant:
                tenant.is_active = False
        await db.commit()


@router.post("/culqi")
async def culqi_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    raw_body = await request.body()
    signature = request.headers.get("X-Culqi-Signature")
    if not _verify(raw_body, signature):
        return Response(status_code=403)

    event = await request.json()
    action = CulqiService.handle_webhook_event(event)
    logger.info("culqi_webhook", action=action, event_type=event.get("type"))
    if action != "ignore":
        background_tasks.add_task(_apply_action, action, event)
    return Response(status_code=200)
