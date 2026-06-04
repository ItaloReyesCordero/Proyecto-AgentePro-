from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentTenant, DbSession
from app.schemas.metrics import (
    CostBreakdown,
    LeadsFunnelPoint,
    MessageVolumePoint,
    MetricsSummary,
)
from app.services import metrics_service

router = APIRouter(prefix="/metrics", tags=["metrics"])

Period = str


@router.get("/summary", response_model=MetricsSummary)
async def summary(
    tenant: CurrentTenant, db: DbSession, period: Period = Query("7d")
) -> MetricsSummary:
    return await metrics_service.get_summary(db, tenant.id, period)


@router.get("/message-volume", response_model=list[MessageVolumePoint])
async def message_volume(
    tenant: CurrentTenant, db: DbSession, period: Period = Query("7d")
) -> list[MessageVolumePoint]:
    return await metrics_service.get_message_volume(db, tenant.id, period)


@router.get("/messages-volume", response_model=list[MessageVolumePoint])
async def message_volume_alias(
    tenant: CurrentTenant, db: DbSession, period: Period = Query("7d")
) -> list[MessageVolumePoint]:
    return await metrics_service.get_message_volume(db, tenant.id, period)


@router.get("/leads-funnel", response_model=list[LeadsFunnelPoint])
async def leads_funnel(tenant: CurrentTenant, db: DbSession) -> list[LeadsFunnelPoint]:
    return await metrics_service.get_leads_funnel(db, tenant.id)


@router.get("/costs", response_model=CostBreakdown)
async def costs(
    tenant: CurrentTenant, db: DbSession, period: Period = Query("30d")
) -> CostBreakdown:
    return await metrics_service.get_costs(db, tenant.id, period)
