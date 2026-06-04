from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_webhook_verify_token,
    hash_password,
    verify_password,
)
from app.dependencies import CurrentUser, DbSession
from app.models.agent_config import AgentConfig
from app.models.password_reset import PasswordResetRequest, ResetStatus
from app.models.tenant import BusinessType, PlanType, Tenant
from app.models.user import User, UserRole
from app.models.voice_config import VoiceConfig
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetRequestIn,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{slug[:40]}-{secrets.token_hex(3)}"


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: DbSession) -> TokenPair:
    """Registro para onboarding manual: crea tenant + usuario propietario."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        business_type = BusinessType(payload.business_type)
    except ValueError:
        business_type = BusinessType.OTHER

    slug = _slugify(payload.business_name)
    tenant = Tenant(
        name=payload.business_name,
        slug=slug,
        business_type=business_type,
        plan=PlanType.TRIAL,
        webhook_verify_token=generate_webhook_verify_token(slug),
        trial_ends_at=datetime.now(tz=timezone.utc) + timedelta(days=14),
    )
    db.add(tenant)
    await db.flush()

    db.add(AgentConfig(tenant_id=tenant.id, agent_name="María"))
    db.add(VoiceConfig(tenant_id=tenant.id, agent_name="María"))

    user = User(
        tenant_id=tenant.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.OWNER,
    )
    db.add(user)
    await db.flush()

    return _build_token_pair(user)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: DbSession) -> TokenPair:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tu cuenta está desactivada. Contacta al administrador.",
        )
    user.last_login_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return _build_token_pair(user)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest) -> AccessTokenResponse:
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access = create_access_token(
        {"sub": data.get("sub"), "tenant_id": data.get("tenant_id")}
    )
    return AccessTokenResponse(access_token=access)


@router.post("/logout", response_model=MessageResponse)
async def logout(_user: CurrentUser) -> MessageResponse:
    # Sin almacén de refresh tokens; el cliente descarta los tokens.
    return MessageResponse(message="Sesión cerrada")


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> User:
    return user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest, user: CurrentUser, db: DbSession
) -> MessageResponse:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=422, detail="La nueva contraseña es muy corta")
    user.hashed_password = hash_password(payload.new_password)
    await db.flush()
    return MessageResponse(message="Contraseña actualizada")


@router.post("/password-reset-request", response_model=MessageResponse)
async def password_reset_request(
    payload: PasswordResetRequestIn, db: DbSession
) -> MessageResponse:
    """Recuperación de contraseña para DUEÑOS de negocio.

    No revela si el correo existe (respuesta siempre genérica). Si existe y no es
    una cuenta superadmin, registra una solicitud PENDIENTE para que el super
    admin la revise, confirme la identidad del dueño y genere una clave nueva.
    Las cuentas superadmin no entran a este flujo a propósito.
    """
    generic = MessageResponse(
        message=(
            "Si el correo corresponde a un negocio, registramos tu solicitud. "
            "El administrador la revisará y te entregará una contraseña nueva."
        )
    )
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or user.role == UserRole.SUPERADMIN:
        return generic

    # No duplicar: si ya hay una solicitud pendiente para este usuario, reutilizar.
    existing = await db.execute(
        select(PasswordResetRequest).where(
            PasswordResetRequest.user_id == user.id,
            PasswordResetRequest.status == ResetStatus.PENDING,
        )
    )
    if existing.scalar_one_or_none() is None:
        db.add(
            PasswordResetRequest(
                user_id=user.id, tenant_id=user.tenant_id, email=user.email
            )
        )
        await db.flush()
    return generic


def _build_token_pair(user: User) -> TokenPair:
    claims = {"sub": str(user.id), "tenant_id": str(user.tenant_id) if user.tenant_id else None}
    return TokenPair(
        access_token=create_access_token(claims),
        refresh_token=create_refresh_token(claims),
        user=UserOut.model_validate(user),
    )
