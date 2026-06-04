from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.services.crm.hubspot_client import HubSpotClient
from app.utils.helpers import derive_lead_stage, enum_value
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def sync_contact_to_hubspot(db: AsyncSession, contact: Contact, tenant_id: str) -> str | None:
    """Crea/actualiza el contacto en HubSpot y guarda el id en el modelo."""
    client = HubSpotClient()
    lead_stage = derive_lead_stage(enum_value(contact.status), contact.qualification_score)
    hubspot_id = await client.create_or_update_contact(
        phone=contact.phone_number or contact.wa_id or "",
        name=contact.full_name,
        email=contact.email,
        lead_score=contact.qualification_score,
        lead_stage=lead_stage,
        source=enum_value(contact.primary_channel),
        tenant_id=tenant_id,
    )
    if hubspot_id:
        contact.hubspot_contact_id = hubspot_id
        await db.flush()
    return hubspot_id
