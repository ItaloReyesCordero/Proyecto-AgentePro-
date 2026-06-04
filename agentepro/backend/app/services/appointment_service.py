from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.plans import FEATURE_APPOINTMENTS, plan_has_feature
from app.models.appointment import Appointment, AppointmentSource, AppointmentStatus
from app.models.contact import Contact
from app.models.tenant import Tenant
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Claves que la IA suele poner en key_info_extracted para el servicio / cuándo.
_SERVICE_KEYS = ("service", "servicio", "service_name", "servicio_solicitado")
_WHEN_KEYS = ("when", "cuando", "fecha", "date", "datetime", "appointment_date")
_NAME_KEYS = ("name", "nombre", "customer_name", "cliente")


def parse_when(raw: Any) -> tuple[datetime | None, str | None]:
    """Intenta convertir lo que diga la IA (ISO o texto) en datetime.

    Devuelve (datetime_o_None, texto_crudo). Si no se puede parsear, el datetime
    queda None y se conserva el texto para que el negocio coordine.
    """
    if raw in (None, "", "null"):
        return None, None
    text = str(raw).strip()
    # Intento ISO (admite "2026-06-06", "2026-06-06T17:00", con o sin zona).
    iso = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt, text
    except ValueError:
        return None, text


def _pick(d: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for k in keys:
        v = d.get(k)
        if v:
            return str(v)
    return None


async def create_appointment(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    source: AppointmentSource,
    contact_id: uuid.UUID | None = None,
    customer_name: str | None = None,
    customer_phone: str | None = None,
    service_name: str | None = None,
    scheduled_at: datetime | None = None,
    raw_when: str | None = None,
    notes: str | None = None,
    status: AppointmentStatus = AppointmentStatus.REQUESTED,
) -> Appointment:
    appt = Appointment(
        tenant_id=tenant_id,
        contact_id=contact_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        service_name=service_name,
        scheduled_at=scheduled_at,
        raw_when=raw_when,
        notes=notes,
        status=status,
        source=source,
    )
    db.add(appt)
    await db.flush()
    await db.refresh(appt)
    return appt


async def list_appointments(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    status: str | None = None,
    limit: int = 200,
) -> list[Appointment]:
    stmt = select(Appointment).where(Appointment.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Appointment.status == status)
    stmt = stmt.order_by(
        Appointment.scheduled_at.is_(None),  # las sin fecha al final
        Appointment.scheduled_at.asc(),
        Appointment.created_at.desc(),
    ).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _open_appointment_for_contact(
    db: AsyncSession, tenant_id: uuid.UUID, contact_id: uuid.UUID
) -> Appointment | None:
    """Cita 'viva' (solicitada/confirmada) más reciente del contacto, para no
    duplicar una cita por cada mensaje de la misma conversación."""
    stmt = (
        select(Appointment)
        .where(
            Appointment.tenant_id == tenant_id,
            Appointment.contact_id == contact_id,
            Appointment.status.in_([AppointmentStatus.REQUESTED, AppointmentStatus.CONFIRMED]),
        )
        .order_by(Appointment.created_at.desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def maybe_create_from_agent(
    db: AsyncSession,
    *,
    tenant: Tenant,
    contact: Contact,
    agent_config,
    intent: str,
    appointment_date: Any,
    key_info: dict[str, Any],
    source: AppointmentSource,
) -> Appointment | None:
    """Si el agente detectó intención de cita, crea/actualiza la cita y avisa al
    dueño. Devuelve la cita o None si no aplica.
    """
    key_info = key_info or {}
    # El módulo de Citas solo está en Profesional/Enterprise (y trial). Si el plan
    # no lo incluye, no se crean citas automáticas aunque el cliente las pida.
    if not plan_has_feature(tenant.plan, FEATURE_APPOINTMENTS):
        return None
    has_signal = intent == "appointment" or bool(appointment_date) or bool(_pick(key_info, _WHEN_KEYS))
    if not has_signal:
        return None

    scheduled_at, raw_when = parse_when(appointment_date or _pick(key_info, _WHEN_KEYS))
    service_name = _pick(key_info, _SERVICE_KEYS)
    customer_name = contact.full_name or _pick(key_info, _NAME_KEYS)
    customer_phone = contact.phone_number or contact.wa_id

    existing = await _open_appointment_for_contact(db, tenant.id, contact.id)
    if existing is not None:
        # Actualiza datos si llegaron nuevos (el cliente fue precisando).
        changed = False
        if scheduled_at and existing.scheduled_at != scheduled_at:
            existing.scheduled_at = scheduled_at; changed = True
        if raw_when and existing.raw_when != raw_when:
            existing.raw_when = raw_when; changed = True
        if service_name and not existing.service_name:
            existing.service_name = service_name; changed = True
        if changed:
            await db.flush()
        return existing

    appt = await create_appointment(
        db,
        tenant_id=tenant.id,
        source=source,
        contact_id=contact.id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        service_name=service_name,
        scheduled_at=scheduled_at,
        raw_when=raw_when,
    )
    await notify_owner_new_appointment(tenant, agent_config, appt)
    appt.owner_notified = True
    await db.flush()
    return appt


def _format_when(appt: Appointment) -> str:
    if appt.scheduled_at:
        return appt.scheduled_at.strftime("%d/%m/%Y %H:%M")
    return appt.raw_when or "por coordinar"


async def notify_owner_new_appointment(tenant: Tenant, agent_config, appt: Appointment) -> None:
    """Avisa al dueño de una nueva cita: panel (socket) + email + WhatsApp (best-effort)."""
    from app.services.notification_service import emit_event, send_email
    from app.services.whatsapp.sender import send_whatsapp_message

    service = appt.service_name or "servicio"
    when = _format_when(appt)
    who = appt.customer_name or appt.customer_phone or "Un cliente"

    # 1. Panel en tiempo real
    try:
        await emit_event(
            str(tenant.id),
            "new_appointment",
            {
                "id": str(appt.id),
                "customer": who,
                "service": service,
                "when": when,
                "source": appt.source.value if hasattr(appt.source, "value") else appt.source,
            },
        )
    except Exception as exc:
        logger.error("appt_socket_failed", error=str(exc))

    # 2. Email al dueño (Resend)
    email = getattr(agent_config, "escalation_email", None)
    if email:
        await send_email(
            to=email,
            subject=f"📅 Nueva cita: {service} — {when}",
            html=(
                f"<h2>Tienes una nueva solicitud de cita</h2>"
                f"<p><b>Cliente:</b> {who}</p>"
                f"<p><b>Servicio:</b> {service}</p>"
                f"<p><b>Cuándo:</b> {when}</p>"
                f"<p>Ingresa al panel → <b>Citas</b> para confirmarla.</p>"
            ),
        )

    # 3. WhatsApp al dueño (best-effort)
    owner_wa = getattr(agent_config, "escalation_phone", None) or settings.PAYMENT_CONTACT_WHATSAPP
    if owner_wa:
        msg = (
            f"📅 *Nueva cita* en {tenant.name}\n"
            f"Cliente: {who}\n"
            f"Servicio: {service}\n"
            f"Cuándo: {when}\n\n"
            f"Confírmala en tu panel → Citas."
        )
        try:
            await send_whatsapp_message(tenant, owner_wa, msg)
        except Exception as exc:
            logger.error("appt_owner_wa_failed", error=str(exc))
