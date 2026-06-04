from __future__ import annotations

import modal

from app.modal_tasks.app import app, image, secrets


@app.function(image=image, schedule=modal.Cron("0 14 * * *"), secrets=secrets)
async def follow_up_leads() -> dict[str, int]:
    """Seguimiento diario de leads tibios/calientes sin respuesta (09:00 hora Perú = 14:00 UTC).

    Recorre tenants con la automatización de follow-up activa y envía un mensaje
    personalizado generado por Claude a contactos sin interacción reciente.
    """
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.automation import Automation, AutomationStatus, AutomationType
    from app.models.contact import Contact
    from app.models.tenant import Tenant
    from app.services.ai.agent import AIAgentService
    from app.services.whatsapp.sender import send_whatsapp_message

    agent = AIAgentService()
    sent = 0
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=24)

    async with AsyncSessionLocal() as db:
        tenants = (
            await db.execute(
                select(Tenant)
                .join(Automation, Automation.tenant_id == Tenant.id)
                .where(
                    Tenant.is_active.is_(True),
                    Automation.automation_type == AutomationType.FOLLOW_UP,
                    Automation.status == AutomationStatus.ACTIVE,
                )
            )
        ).scalars().unique().all()

        for tenant in tenants:
            contacts = (
                await db.execute(
                    select(Contact).where(
                        Contact.tenant_id == tenant.id,
                        Contact.qualification_score >= 34,
                        Contact.opted_in.is_(True),
                        Contact.last_interaction_at < cutoff,
                    ).limit(50)
                )
            ).scalars().all()

            for contact in contacts:
                cfg = tenant.agent_config
                message = await agent.generate_quick_reply(
                    context=(
                        f"Genera un mensaje breve de seguimiento para {contact.full_name or 'el cliente'} "
                        f"que mostró interés pero no respondió en 24h. No seas invasivo."
                    ),
                    agent_config=cfg,
                ) if cfg else "Hola, ¿seguimos en contacto? Quedamos atentos a cualquier consulta."
                to = contact.wa_id or contact.phone_number
                if to and await send_whatsapp_message(tenant, to, message):
                    contact.last_interaction_at = datetime.now(tz=timezone.utc)
                    sent += 1
        await db.commit()

    return {"messages_sent": sent}


@app.function(image=image, secrets=secrets)
async def trigger_followup_for_contact(contact_id: str, tenant_id: str, reason: str) -> bool:
    """Disparo manual de follow-up para un contacto específico."""
    import uuid

    from app.database import AsyncSessionLocal
    from app.models.tenant import Tenant
    from app.services.contact_service import get_contact
    from app.services.ai.agent import AIAgentService
    from app.services.whatsapp.sender import send_whatsapp_message

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tenant_id))
        contact = await get_contact(db, uuid.UUID(tenant_id), uuid.UUID(contact_id))
        if not tenant or not contact:
            return False
        message = await AIAgentService().generate_quick_reply(
            context=f"Seguimiento ({reason}) para {contact.full_name or 'el cliente'}.",
            agent_config=tenant.agent_config,
        )
        to = contact.wa_id or contact.phone_number
        ok = bool(to) and await send_whatsapp_message(tenant, to, message)
        await db.commit()
        return ok
