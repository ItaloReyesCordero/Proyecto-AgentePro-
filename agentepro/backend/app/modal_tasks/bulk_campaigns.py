from __future__ import annotations

import modal

from app.modal_tasks.app import app, image, secrets


@app.function(image=image, secrets=secrets)
async def run_bulk_campaign(
    tenant_id: str, message_template: str, target_tags: list[str] | None = None
) -> dict[str, int]:
    """Envía una campaña masiva a contactos del tenant que aceptaron contacto.

    Respeta el opt-in y aplica un throttle simple para no saturar la API de Meta.
    """
    import asyncio
    import uuid

    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.contact import Contact
    from app.models.tenant import Tenant
    from app.services.whatsapp.sender import send_whatsapp_message

    sent = 0
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(tenant_id))
        if tenant is None or not tenant.is_active:
            return {"sent": 0}

        conditions = [Contact.tenant_id == tenant.id, Contact.opted_in.is_(True)]
        contacts = (await db.execute(select(Contact).where(*conditions))).scalars().all()

        for contact in contacts:
            if target_tags and not set(target_tags) & set(contact.tags or []):
                continue
            to = contact.wa_id or contact.phone_number
            if not to:
                continue
            personalized = message_template.replace(
                "{nombre}", contact.first_name or contact.full_name or ""
            )
            if await send_whatsapp_message(tenant, to, personalized):
                sent += 1
            await asyncio.sleep(0.25)  # throttle ~4 msg/s

    return {"sent": sent}
