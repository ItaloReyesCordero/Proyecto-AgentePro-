from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from app.config import settings
from app.core.security import verify_admin_key
from app.dependencies import DbSession
from app.models.user import User
from app.schemas.tenant import ProvisionRequest, ProvisionResponse
from app.services.culqi_service import CulqiService
from app.services.provisioning.tenant_provisioner import TenantProvisioner

router = APIRouter(tags=["provisioning"])

_provisioner = TenantProvisioner()
_culqi = CulqiService()


@router.post("/signup", response_model=ProvisionResponse)
async def signup(payload: ProvisionRequest, db: DbSession) -> ProvisionResponse:
    """Alta self-service: el negocio se registra, elige plan y queda aprovisionado.

    El cobro se procesa con Culqi (simulado mientras no haya CULQI_SECRET_KEY).
    El dueño debe enviar `password` para luego iniciar sesión en el dashboard.
    """
    if not settings.ALLOW_FREE_SIGNUP and not payload.culqi_token:
        raise HTTPException(status_code=403, detail="Se requiere pago para registrarse")
    if not payload.password or len(payload.password) < 6:
        raise HTTPException(status_code=422, detail="Define una contraseña de al menos 6 caracteres")

    existing = await db.execute(select(User).where(User.email == payload.owner_email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ese email ya está registrado")

    try:
        await _culqi.charge(payload.culqi_token or "tkn_signup", payload.plan, str(payload.owner_email))
    except Exception as exc:
        raise HTTPException(status_code=402, detail=f"Pago rechazado: {exc}") from exc

    result = await _provisioner.provision_new_tenant(payload, db)
    return ProvisionResponse(**result)


@router.post("/provision", response_model=ProvisionResponse)
async def provision(
    payload: ProvisionRequest,
    db: DbSession,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> ProvisionResponse:
    """Procesa el pago (si hay token) y aprovisiona todo el tenant.

    Accesible con un culqi_token válido o con la clave de administración.
    """
    is_admin = bool(x_admin_key and verify_admin_key(x_admin_key))
    if not is_admin and not payload.culqi_token:
        raise HTTPException(status_code=403, detail="Pago o clave de admin requeridos")

    # 1. Cobro
    if payload.culqi_token:
        try:
            await _culqi.charge(payload.culqi_token, payload.plan, str(payload.owner_email))
        except Exception as exc:
            raise HTTPException(status_code=402, detail=f"Pago rechazado: {exc}") from exc

    # 2. Provisioning completo (con rollback interno)
    result = await _provisioner.provision_new_tenant(payload, db)
    return ProvisionResponse(**result)
