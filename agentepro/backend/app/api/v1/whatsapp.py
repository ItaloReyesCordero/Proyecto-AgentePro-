from __future__ import annotations

from pydantic import BaseModel

from fastapi import APIRouter

from app.core.security import generate_webhook_verify_token
from app.dependencies import CurrentTenant, DbSession
from app.utils.encryption import encrypt
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class WhatsAppConnectRequest(BaseModel):
    phone_number_id: str
    waba_id: str | None = None
    access_token: str


class WhatsAppStatus(BaseModel):
    connected: bool
    phone_number_id: str | None = None
    webhook_url: str
    verify_token: str | None = None
    verified: bool | None = None


@router.post("/connect", response_model=WhatsAppStatus)
async def connect_whatsapp(
    payload: WhatsAppConnectRequest, tenant: CurrentTenant, db: DbSession
) -> WhatsAppStatus:
    """Guarda las credenciales de WhatsApp del negocio (token cifrado con Fernet)."""
    tenant.phone_number_id = payload.phone_number_id
    tenant.waba_id = payload.waba_id
    tenant.whatsapp_access_token = encrypt(payload.access_token)
    if not tenant.webhook_verify_token:
        tenant.webhook_verify_token = generate_webhook_verify_token(tenant.slug)
    await db.flush()
    return await _status(tenant)


@router.get("/status", response_model=WhatsAppStatus)
async def whatsapp_status(tenant: CurrentTenant) -> WhatsAppStatus:
    return await _status(tenant)


@router.post("/disconnect", response_model=WhatsAppStatus)
async def disconnect_whatsapp(tenant: CurrentTenant, db: DbSession) -> WhatsAppStatus:
    tenant.phone_number_id = None
    tenant.waba_id = None
    tenant.whatsapp_access_token = None
    await db.flush()
    return await _status(tenant)


async def _status(tenant: CurrentTenant) -> WhatsAppStatus:
    from app.config import settings

    backend_base = settings.FRONTEND_URL.replace(":5173", ":8000")
    webhook_url = f"{backend_base}/webhooks/whatsapp/{tenant.slug}"
    connected = bool(tenant.phone_number_id and tenant.whatsapp_access_token)
    return WhatsAppStatus(
        connected=connected,
        phone_number_id=tenant.phone_number_id,
        webhook_url=webhook_url,
        verify_token=tenant.webhook_verify_token,
        verified=connected,
    )
