from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.dependencies import CurrentTenant, DbSession
from app.models.agent_config import AgentConfig
from app.services.notion import notion_client, notion_sync
from app.utils.encryption import encrypt
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/notion", tags=["notion"])


class NotionConnectRequest(BaseModel):
    api_key: str
    database_id: str


class NotionStatus(BaseModel):
    connected: bool
    database_id: str | None = None
    last_synced_at: datetime | None = None
    services_count: int = 0


class NotionSyncResult(BaseModel):
    synced: int
    last_synced_at: datetime | None = None


def _normalize_database_id(raw: str) -> str:
    """Acepta un ID con guiones, sin guiones, o pegado de una URL de Notion."""
    value = (raw or "").strip()
    # Si pegaron una URL completa, el ID es el último tramo de 32 hex.
    if "notion.so" in value or "/" in value:
        value = value.rstrip("/").split("/")[-1]
    # Las URLs traen "Titulo-<32hex>?..." → quedarse con los 32 hex finales.
    value = value.split("?")[0]
    if "-" in value and len(value.replace("-", "")) >= 32:
        value = value.split("-")[-1]
    return value


async def _services_count(tenant: CurrentTenant, db: DbSession) -> int:
    result = await db.execute(
        select(AgentConfig.services).where(AgentConfig.tenant_id == tenant.id)
    )
    services = result.scalar_one_or_none()
    return len(services) if isinstance(services, list) else 0


async def _status(tenant: CurrentTenant, db: DbSession) -> NotionStatus:
    return NotionStatus(
        connected=bool(tenant.notion_api_key and tenant.notion_database_id),
        database_id=tenant.notion_database_id,
        last_synced_at=tenant.notion_last_synced_at,
        services_count=await _services_count(tenant, db),
    )


@router.get("/status", response_model=NotionStatus)
async def notion_status(tenant: CurrentTenant, db: DbSession) -> NotionStatus:
    return await _status(tenant, db)


@router.post("/connect", response_model=NotionSyncResult)
async def connect_notion(
    payload: NotionConnectRequest, tenant: CurrentTenant, db: DbSession
) -> NotionSyncResult:
    """Guarda las credenciales de Notion (token cifrado) y hace una primera
    sincronización del catálogo hacia el agente."""
    database_id = _normalize_database_id(payload.database_id)
    if not payload.api_key.strip() or not database_id:
        raise HTTPException(status_code=422, detail="Falta el token o el ID de la base de Notion.")

    tenant.notion_api_key = encrypt(payload.api_key.strip())
    tenant.notion_database_id = database_id
    await db.flush()

    try:
        synced = await notion_sync.sync_tenant_catalog(tenant, db)
    except notion_client.NotionError as exc:
        # Credenciales malas: no las dejamos guardadas a medias.
        tenant.notion_api_key = None
        tenant.notion_database_id = None
        await db.flush()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return NotionSyncResult(synced=synced, last_synced_at=tenant.notion_last_synced_at)


@router.post("/sync", response_model=NotionSyncResult)
async def sync_notion(tenant: CurrentTenant, db: DbSession) -> NotionSyncResult:
    """Vuelve a leer la Notion del negocio y actualiza el catálogo del agente."""
    if not tenant.notion_api_key or not tenant.notion_database_id:
        raise HTTPException(status_code=400, detail="Notion no está conectado.")
    try:
        synced = await notion_sync.sync_tenant_catalog(tenant, db)
    except notion_client.NotionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return NotionSyncResult(synced=synced, last_synced_at=tenant.notion_last_synced_at)


@router.post("/disconnect", response_model=NotionStatus)
async def disconnect_notion(tenant: CurrentTenant, db: DbSession) -> NotionStatus:
    tenant.notion_api_key = None
    tenant.notion_database_id = None
    tenant.notion_last_synced_at = None
    await db.flush()
    return await _status(tenant, db)
