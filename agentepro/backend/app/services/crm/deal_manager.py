from __future__ import annotations

from app.services.crm.hubspot_client import HubSpotClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def create_deal_for_hot_lead(
    hubspot_contact_id: str,
    business_name: str,
    amount: float | None = None,
) -> str | None:
    """Crea automáticamente un deal cuando un lead se vuelve caliente."""
    if not hubspot_contact_id:
        return None
    client = HubSpotClient()
    deal_name = f"Lead caliente — {business_name}"
    return await client.create_deal(
        contact_id=hubspot_contact_id,
        deal_name=deal_name,
        stage="appointmentscheduled",
        amount=amount,
    )
