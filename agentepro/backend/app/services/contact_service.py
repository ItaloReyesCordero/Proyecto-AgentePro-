from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact, ContactChannel, ContactStatus
from app.utils.helpers import lead_stage_to_contact_status, normalize_phone
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_or_create_contact(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    wa_id: str,
    name: str | None = None,
    channel: str = "whatsapp",
) -> Contact:
    """Busca un contacto por wa_id dentro del tenant; lo crea si no existe."""
    result = await db.execute(
        select(Contact).where(Contact.tenant_id == tenant_id, Contact.wa_id == wa_id)
    )
    contact = result.scalar_one_or_none()
    if contact is not None:
        if name and not contact.full_name:
            contact.full_name = name
        contact.last_interaction_at = datetime.now(tz=timezone.utc)
        return contact

    channel_enum = {
        "whatsapp": ContactChannel.WHATSAPP,
        "instagram": ContactChannel.INSTAGRAM,
        "instagram_dm": ContactChannel.INSTAGRAM,
        "voice": ContactChannel.VOICE,
    }.get(channel, ContactChannel.WHATSAPP)

    contact = Contact(
        tenant_id=tenant_id,
        wa_id=wa_id,
        phone_number=normalize_phone(wa_id),
        full_name=name,
        status=ContactStatus.LEAD,
        primary_channel=channel_enum,
        last_interaction_at=datetime.now(tz=timezone.utc),
    )
    db.add(contact)
    await db.flush()
    logger.info("contact_created", tenant_id=str(tenant_id), wa_id=wa_id)
    return contact


def apply_lead_update(contact: Contact, lead_score: int, lead_stage: str) -> None:
    """Actualiza la calificación del contacto preservando el máximo histórico de score."""
    contact.qualification_score = max(contact.qualification_score or 0, lead_score)
    if lead_stage:
        contact.status = ContactStatus(lead_stage_to_contact_status(lead_stage))
    if contact.qualification_score >= 67:
        contact.is_qualified = True


async def get_contact(db: AsyncSession, tenant_id: uuid.UUID, contact_id: uuid.UUID) -> Contact | None:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()
