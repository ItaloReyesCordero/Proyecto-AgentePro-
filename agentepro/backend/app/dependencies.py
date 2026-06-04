from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AccountSuspendedError,
    FeatureNotInPlanError,
    PaymentOverdueError,
    TrialExpiredError,
)
from app.core.plans import plan_has_feature
from app.core.security import decode_token, oauth2_scheme, verify_admin_key
from app.core.tenant_scope import set_session_tenant
from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    """Resuelve el usuario autenticado a partir del JWT de acceso."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )
    result = await db.execute(select(User).where(User.id == uuid.UUID(str(user_id))))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_tenant(
    user: CurrentUser,
    db: DbSession,
) -> Tenant:
    """Devuelve el tenant asociado al usuario autenticado."""
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned",
        )
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    if not tenant.is_active:
        # Desactivado por el admin: 402 con código para que el front redirija a
        # la pantalla de "cuenta suspendida" en vez de romper el dashboard.
        raise AccountSuspendedError()
    if tenant.is_trial_expired:
        raise TrialExpiredError()
    if tenant.billing_suspended:
        raise PaymentOverdueError()
    # Activa el aislamiento por tenant en esta sesión: a partir de aquí toda
    # consulta SELECT se filtra automáticamente por este tenant (ver tenant_scope).
    set_session_tenant(db, tenant.id)
    return tenant


CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]


def require_feature(feature: str):
    """Crea una dependencia que bloquea (402 FEATURE_LOCKED) si el plan del
    negocio NO incluye ese módulo. Se usa como dependencia a nivel de router:

        router = APIRouter(..., dependencies=[Depends(require_feature(FEATURE_VOICE))])
    """

    async def _guard(tenant: CurrentTenant) -> Tenant:
        if not plan_has_feature(tenant.plan, feature):
            raise FeatureNotInPlanError(feature)
        return tenant

    return _guard


async def require_platform_admin(
    db: DbSession,
    x_admin_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Permite acceso de plataforma con la ADMIN_SECRET_KEY **o** con un JWT
    cuyo usuario tenga rol `superadmin`. Así el panel web del fundador puede
    usar su token Bearer normal."""
    if x_admin_key and verify_admin_key(x_admin_key):
        return
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except HTTPException:
            payload = None
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                user = await db.get(User, uuid.UUID(str(user_id)))
                if user and user.is_active and user.role == UserRole.SUPERADMIN:
                    return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Platform admin access required",
    )


# Compatibilidad: alias antiguo basado solo en header.
require_admin = require_platform_admin
AdminGuard = Annotated[None, Depends(require_platform_admin)]
