from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from app.core.plans import FEATURE_VOICE
from app.dependencies import CurrentTenant, DbSession, require_feature
from app.models.call import Call
from app.models.call_summary import CallSummary
from app.models.contact import Contact
from app.models.tenant import Tenant
from app.schemas.call import CallOut, CallSummaryOut, OutboundCallRequest
from app.schemas.common import PaginatedResponse
from app.services import call_service
from app.services.contact_service import get_contact
from app.services.voice.outbound_caller import OutboundCallError, call_lead

router = APIRouter(
    prefix="/calls",
    tags=["calls"],
    dependencies=[Depends(require_feature(FEATURE_VOICE))],
)


async def _load(db: DbSession, call: Call) -> tuple[Contact | None, CallSummary | None]:
    contact = await db.get(Contact, call.contact_id) if call.contact_id else None
    summary_res = await db.execute(select(CallSummary).where(CallSummary.call_id == call.id))
    return contact, summary_res.scalar_one_or_none()


async def _require(db: DbSession, tenant: Tenant, call_id: uuid.UUID) -> Call:
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.tenant_id == tenant.id)
    )
    call = result.scalar_one_or_none()
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.get("", response_model=PaginatedResponse[CallOut])
async def list_calls(
    tenant: CurrentTenant,
    db: DbSession,
    direction: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[CallOut]:
    conditions = [Call.tenant_id == tenant.id]
    if direction:
        conditions.append(Call.direction == direction)
    total_res = await db.execute(select(func.count(Call.id)).where(*conditions))
    total = int(total_res.scalar() or 0)
    result = await db.execute(
        select(Call)
        .where(*conditions)
        .order_by(Call.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    items = []
    for call in result.scalars().all():
        contact, summary = await _load(db, call)
        items.append(CallOut.from_model(call, contact, summary))
    return PaginatedResponse.build(items, total, page, per_page)


@router.get("/{call_id}", response_model=CallOut)
async def get_call(call_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> CallOut:
    call = await _require(db, tenant, call_id)
    contact, summary = await _load(db, call)
    return CallOut.from_model(call, contact, summary)


@router.get("/{call_id}/recording")
async def get_recording(call_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> dict[str, str | None]:
    call = await _require(db, tenant, call_id)
    return {"recording_url": call.recording_url}


@router.get("/{call_id}/summary", response_model=CallSummaryOut)
async def get_summary(call_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> CallSummaryOut:
    call = await _require(db, tenant, call_id)
    _, summary = await _load(db, call)
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not available yet")
    return CallSummaryOut.from_model(summary)


@router.post("/outbound", response_model=CallOut)
async def start_outbound_call(
    payload: OutboundCallRequest, tenant: CurrentTenant, db: DbSession
) -> CallOut:
    contact = None
    if payload.contact_id:
        contact = await get_contact(db, tenant.id, payload.contact_id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
    if contact is None:
        raise HTTPException(status_code=400, detail="contact_id requerido para llamada saliente")
    try:
        call = await call_lead(db, tenant, contact, reason=payload.reason)
    except OutboundCallError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CallOut.from_model(call, contact)
