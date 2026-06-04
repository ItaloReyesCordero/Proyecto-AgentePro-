from __future__ import annotations

from app.services.crm.hubspot_client import HubSpotClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Etapas internas de outcome -> dealstage de HubSpot.
_STAGE_MAP = {
    "appointment_booked": "appointmentscheduled",
    "info_provided": "qualifiedtobuy",
    "sale": "closedwon",
    "no_interest": "closedlost",
    "follow_up_needed": "presentationscheduled",
    "escalated": "qualifiedtobuy",
}


async def update_deal_stage(deal_id: str, outcome: str) -> bool:
    if not deal_id:
        return False
    client = HubSpotClient()
    stage = _STAGE_MAP.get(outcome, "qualifiedtobuy")
    result = await client._post(
        f"/crm/v3/objects/deals/{deal_id}", {"properties": {"dealstage": stage}}
    )
    return result is not None
