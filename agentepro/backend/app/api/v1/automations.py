from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.core.plans import FEATURE_AUTOMATIONS
from app.dependencies import CurrentTenant, DbSession, require_feature
from app.models.automation import Automation, AutomationStatus
from app.models.automation_run import AutomationRun
from app.models.tenant import Tenant
from app.schemas.automation import AutomationOut, AutomationUpdate
from app.schemas.common import MessageResponse

router = APIRouter(
    prefix="/automations",
    tags=["automations"],
    dependencies=[Depends(require_feature(FEATURE_AUTOMATIONS))],
)


async def _require(db: DbSession, tenant: Tenant, automation_id: uuid.UUID) -> Automation:
    result = await db.execute(
        select(Automation).where(
            Automation.id == automation_id, Automation.tenant_id == tenant.id
        )
    )
    automation = result.scalar_one_or_none()
    if automation is None:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation


async def _recent_runs(db: DbSession, automation_id: uuid.UUID) -> list[AutomationRun]:
    result = await db.execute(
        select(AutomationRun)
        .where(AutomationRun.automation_id == automation_id)
        .order_by(AutomationRun.created_at.desc())
        .limit(10)
    )
    return list(result.scalars().all())


@router.get("", response_model=list[AutomationOut])
async def list_automations(tenant: CurrentTenant, db: DbSession) -> list[AutomationOut]:
    result = await db.execute(
        select(Automation)
        .where(Automation.tenant_id == tenant.id)
        .order_by(Automation.created_at.asc())
    )
    out: list[AutomationOut] = []
    for automation in result.scalars().all():
        runs = await _recent_runs(db, automation.id)
        out.append(AutomationOut.from_model(automation, runs))
    return out


@router.patch("/{automation_id}", response_model=AutomationOut)
async def update_automation(
    automation_id: uuid.UUID, payload: AutomationUpdate, tenant: CurrentTenant, db: DbSession
) -> AutomationOut:
    automation = await _require(db, tenant, automation_id)
    if payload.is_active is not None:
        automation.status = (
            AutomationStatus.ACTIVE if payload.is_active else AutomationStatus.PAUSED
        )
    if payload.name is not None:
        automation.name = payload.name
    if payload.description is not None:
        automation.description = payload.description
    if payload.trigger_config is not None:
        automation.trigger_config = payload.trigger_config
    await db.flush()
    runs = await _recent_runs(db, automation.id)
    return AutomationOut.from_model(automation, runs)


@router.get("/{automation_id}/runs", response_model=list[dict])
async def list_runs(
    automation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> list[dict]:
    await _require(db, tenant, automation_id)
    runs = await _recent_runs(db, automation_id)
    return [
        {
            "id": str(r.id),
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "messages_sent": r.messages_sent,
            "created_at": r.created_at.isoformat(),
        }
        for r in runs
    ]


@router.post("/{automation_id}/run", response_model=MessageResponse)
async def run_automation(
    automation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> MessageResponse:
    automation = await _require(db, tenant, automation_id)
    run = AutomationRun(automation_id=automation.id, tenant_id=tenant.id)
    db.add(run)
    automation.total_runs = (automation.total_runs or 0) + 1
    await db.flush()
    # La ejecución real se delega a Modal/Celery; aquí se registra el disparo manual.
    return MessageResponse(message="Automatización encolada para ejecución")
