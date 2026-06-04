from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import CurrentTenant, DbSession
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionOut

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionOut)
async def get_my_subscription(tenant: CurrentTenant, db: DbSession) -> Subscription:
    result = await db.execute(
        select(Subscription).where(Subscription.tenant_id == tenant.id)
    )
    subscription = result.scalar_one_or_none()
    if subscription is None:
        raise HTTPException(status_code=404, detail="No subscription found")
    return subscription
