from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.core.plans import FEATURE_APPOINTMENTS
from app.dependencies import CurrentTenant, DbSession, require_feature
from app.models.appointment import Appointment, AppointmentSource, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.services import appointment_service

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    dependencies=[Depends(require_feature(FEATURE_APPOINTMENTS))],
)


@router.get("", response_model=list[AppointmentOut])
async def list_appointments(
    tenant: CurrentTenant,
    db: DbSession,
    status: str | None = Query(default=None),
) -> list[AppointmentOut]:
    appts = await appointment_service.list_appointments(db, tenant.id, status=status)
    return [AppointmentOut.from_model(a) for a in appts]


@router.post("", response_model=AppointmentOut, status_code=201)
async def create_appointment(
    payload: AppointmentCreate, tenant: CurrentTenant, db: DbSession
) -> AppointmentOut:
    appt = await appointment_service.create_appointment(
        db,
        tenant_id=tenant.id,
        source=AppointmentSource.MANUAL,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        service_name=payload.service_name,
        scheduled_at=payload.scheduled_at,
        raw_when=payload.raw_when,
        notes=payload.notes,
        status=AppointmentStatus.CONFIRMED,
    )
    return AppointmentOut.from_model(appt)


async def _get_owned(db: DbSession, tenant_id: uuid.UUID, appt_id: uuid.UUID) -> Appointment:
    appt = (
        await db.execute(
            select(Appointment).where(
                Appointment.id == appt_id, Appointment.tenant_id == tenant_id
            )
        )
    ).scalar_one_or_none()
    if appt is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return appt


@router.patch("/{appt_id}", response_model=AppointmentOut)
async def update_appointment(
    appt_id: uuid.UUID, payload: AppointmentUpdate, tenant: CurrentTenant, db: DbSession
) -> AppointmentOut:
    appt = await _get_owned(db, tenant.id, appt_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        try:
            appt.status = AppointmentStatus(data.pop("status"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Estado inválido") from exc
    for field, value in data.items():
        setattr(appt, field, value)
    await db.flush()
    await db.refresh(appt)
    return AppointmentOut.from_model(appt)


@router.delete("/{appt_id}", status_code=204)
async def delete_appointment(
    appt_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> None:
    appt = await _get_owned(db, tenant.id, appt_id)
    await db.delete(appt)
    await db.flush()
