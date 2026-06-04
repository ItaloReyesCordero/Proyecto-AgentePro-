from __future__ import annotations

import asyncio

from app.workers.celery_app import celery_app


async def _send_reminders() -> int:
    """Envía un recordatorio por WhatsApp al cliente de cada cita próxima.

    Busca citas con fecha en las próximas `REMINDER_WINDOW_HOURS` horas, que sigan
    vivas (solicitada/confirmada) y a las que aún no se les mandó recordatorio.
    """
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from app.config import settings
    from app.database import AsyncSessionLocal
    from app.models.appointment import Appointment, AppointmentStatus
    from app.models.tenant import Tenant
    from app.services.whatsapp.sender import send_whatsapp_message

    now = datetime.now(tz=timezone.utc)
    horizon = now + timedelta(hours=settings.REMINDER_WINDOW_HOURS)

    sent = 0
    async with AsyncSessionLocal() as db:
        appts = (
            await db.execute(
                select(Appointment).where(
                    Appointment.reminder_sent.is_(False),
                    Appointment.scheduled_at.is_not(None),
                    Appointment.scheduled_at >= now,
                    Appointment.scheduled_at <= horizon,
                    Appointment.status.in_(
                        [AppointmentStatus.REQUESTED, AppointmentStatus.CONFIRMED]
                    ),
                )
            )
        ).scalars().all()

        for appt in appts:
            to = appt.customer_phone
            if not to:
                appt.reminder_sent = True
                continue
            tenant = await db.get(Tenant, appt.tenant_id)
            if tenant is None or not tenant.is_active:
                continue
            when = appt.scheduled_at.strftime("%d/%m a las %H:%M") if appt.scheduled_at else "pronto"
            service = appt.service_name or "tu cita"
            msg = (
                f"¡Hola! 👋 Te recordamos tu cita de *{service}* en {tenant.name} "
                f"el {when}. ¿Confirmas tu asistencia? Responde SÍ o NO. 😊"
            )
            ok = await send_whatsapp_message(tenant, to, msg)
            if ok:
                appt.reminder_sent = True
                sent += 1
        await db.commit()
    return sent


@celery_app.task(name="app.workers.reminder_tasks.send_appointment_reminders")
def send_appointment_reminders() -> int:
    return asyncio.run(_send_reminders())


@celery_app.task(name="app.workers.reminder_tasks.send_followup_reminder")
def send_followup_reminder(tenant_id: str, contact_id: str, message: str) -> bool:
    import uuid

    from app.database import AsyncSessionLocal
    from app.models.tenant import Tenant
    from app.services.contact_service import get_contact
    from app.services.whatsapp.sender import send_whatsapp_message

    async def _run() -> bool:
        async with AsyncSessionLocal() as db:
            tenant = await db.get(Tenant, uuid.UUID(tenant_id))
            contact = await get_contact(db, uuid.UUID(tenant_id), uuid.UUID(contact_id))
            if not tenant or not contact:
                return False
            to = contact.wa_id or contact.phone_number
            return bool(to) and await send_whatsapp_message(tenant, to, message)

    return asyncio.run(_run())
