from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_config import AgentConfig
from app.models.tenant import Tenant
from app.services.notion import notion_client
from app.utils.encryption import decrypt_if_value
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def sync_tenant_catalog(tenant: Tenant, db: AsyncSession) -> int:
    """Trae el catálogo desde la Notion del tenant y lo vuelca en
    ``agent_config.services`` (lo que lee el agente). Devuelve cuántos servicios
    quedaron sincronizados.

    Lanza :class:`notion_client.NotionError` si las credenciales son inválidas.
    """
    api_key = decrypt_if_value(tenant.notion_api_key)
    if not api_key or not tenant.notion_database_id:
        return 0

    services = await notion_client.fetch_catalog(api_key, tenant.notion_database_id)

    result = await db.execute(
        select(AgentConfig).where(AgentConfig.tenant_id == tenant.id)
    )
    config = result.scalar_one_or_none()
    if config is None:
        config = AgentConfig(tenant_id=tenant.id, agent_name="María")
        db.add(config)

    config.services = services
    tenant.notion_last_synced_at = datetime.now(tz=timezone.utc)
    await db.flush()
    await db.refresh(config)

    logger.info("notion_synced", tenant_id=str(tenant.id), count=len(services))
    return len(services)
