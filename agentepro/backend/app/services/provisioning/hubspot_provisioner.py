from __future__ import annotations

from app.services.crm.hubspot_client import HubSpotClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def provision_hubspot_company(company_name: str) -> str | None:
    """Crea la empresa del tenant en HubSpot. None si HubSpot no está configurado."""
    client = HubSpotClient()
    if not client._enabled:
        logger.info("hubspot_provision_skipped", company=company_name)
        return None
    return await client.setup_tenant_company(company_name)
