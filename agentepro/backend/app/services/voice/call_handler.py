from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call import Call, CallStatus
from app.models.call_summary import CallSummary
from app.models.tenant import Tenant
from app.schemas.webhook_retell import RetellCallEvent
from app.services import call_service, contact_service
from app.services.ai.call_summarizer import CallSummarizerService
from app.services.crm.hubspot_client import HubSpotClient
from app.services.notification_service import emit_event
from app.utils.logger import get_logger

logger = get_logger(__name__)

_summarizer = CallSummarizerService()


async def handle_call_started(db: AsyncSession, tenant: Tenant, event: RetellCallEvent) -> None:
    existing = await call_service.get_call_by_retell_id(db, event.call_id)
    if existing:
        existing.status = CallStatus.IN_PROGRESS
        await db.flush()
        return
    await call_service.create_call(
        db,
        tenant_id=tenant.id,
        retell_call_id=event.call_id,
        direction=event.direction or "inbound",
        from_number=event.from_number,
        to_number=event.to_number,
        status=CallStatus.IN_PROGRESS,
    )
    await emit_event(
        str(tenant.id),
        "new_call",
        {"call_id": event.call_id, "from_number": event.from_number, "direction": event.direction},
    )


async def handle_call_ended(db: AsyncSession, tenant: Tenant, event: RetellCallEvent) -> None:
    call = await call_service.get_call_by_retell_id(db, event.call_id)
    if call is None:
        call = await call_service.create_call(
            db, tenant_id=tenant.id, retell_call_id=event.call_id,
            direction=event.direction or "inbound",
            from_number=event.from_number, to_number=event.to_number,
        )
    call.status = CallStatus.COMPLETED
    call.ended_at = datetime.now(tz=timezone.utc)
    if event.duration_ms:
        call.duration_seconds = event.duration_ms // 1000
    if event.transcript:
        call.transcription = event.transcript
    if event.recording_url:
        call.recording_url = event.recording_url
    tenant.calls_used_this_month = (tenant.calls_used_this_month or 0) + 1
    await db.flush()
    await emit_event(
        str(tenant.id),
        "call_ended",
        {"call_id": event.call_id, "duration": call.duration_seconds},
    )


async def handle_call_analyzed(db: AsyncSession, tenant: Tenant, event: RetellCallEvent) -> None:
    """Genera el resumen con Claude y sincroniza con HubSpot."""
    call = await call_service.get_call_by_retell_id(db, event.call_id)
    if call is None:
        return
    transcript = event.transcript or call.transcription or ""
    if not transcript.strip():
        return

    summary = await _summarizer.summarize(
        transcript=transcript,
        call_duration_seconds=call.duration_seconds,
        call_direction=str(call.direction.value if hasattr(call.direction, "value") else call.direction),
    )

    call.sentiment = summary.sentiment
    call.intent = summary.intent

    db_summary = CallSummary(
        call_id=call.id,
        summary=summary.summary,
        key_points=summary.key_points,
        action_items=[{"text": summary.next_action}] if summary.next_action else [],
        overall_sentiment=summary.sentiment,
        call_outcome="appointment_booked" if summary.appointment_requested else "info_provided",
        follow_up_required=summary.appointment_requested,
        follow_up_notes=summary.next_action,
        intent_detected=summary.intent,
        tokens_used=summary.tokens_used,
        model_used="claude",
    )
    db.add(db_summary)

    # Actualizar contacto con score de la llamada
    if call.contact_id:
        contact = await contact_service.get_contact(db, tenant.id, call.contact_id)
        if contact:
            contact_service.apply_lead_update(contact, summary.lead_score, summary.lead_stage)
            if contact.hubspot_contact_id:
                try:
                    await HubSpotClient().add_activity_note(
                        contact.hubspot_contact_id,
                        f"Llamada ({call.direction}): {summary.summary}",
                    )
                except Exception as exc:
                    logger.error("hubspot_call_note_failed", error=str(exc))

    # Si en la llamada se pidió una cita, créala y avisa al dueño.
    if summary.appointment_requested:
        try:
            from sqlalchemy import select as _select

            from app.models.agent_config import AgentConfig
            from app.models.appointment import AppointmentSource
            from app.services import appointment_service

            agent_config = (
                await db.execute(_select(AgentConfig).where(AgentConfig.tenant_id == tenant.id))
            ).scalar_one_or_none()
            appt = await appointment_service.create_appointment(
                db,
                tenant_id=tenant.id,
                source=AppointmentSource.VOICE,
                contact_id=call.contact_id,
                customer_phone=call.from_number,
                raw_when=summary.next_action,
                notes=summary.summary,
            )
            if agent_config is not None:
                await appointment_service.notify_owner_new_appointment(tenant, agent_config, appt)
                appt.owner_notified = True
            await db.flush()
        except Exception as exc:
            logger.error("voice_appointment_failed", error=str(exc))

    await db.flush()
    await emit_event(
        str(tenant.id),
        "call_completed",
        {"call_id": event.call_id, "sentiment": summary.sentiment},
    )


async def process_retell_event(db: AsyncSession, tenant: Tenant, event: RetellCallEvent) -> None:
    handlers = {
        "call_started": handle_call_started,
        "call_ended": handle_call_ended,
        "call_analyzed": handle_call_analyzed,
    }
    handler = handlers.get(event.event)
    if handler:
        await handler(db, tenant, event)
    else:
        logger.info("retell_event_ignored", event_type=event.event)
