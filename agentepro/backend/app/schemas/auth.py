from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    business_name: str
    business_type: str = "other"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequestIn(BaseModel):
    """Lo que envía un dueño desde '¿Olvidaste tu contraseña?'."""
    email: EmailStr


class PasswordResetRequestOut(BaseModel):
    """Solicitud de recuperación tal como la ve el super admin."""
    id: uuid.UUID
    email: str
    user_id: uuid.UUID | None
    tenant_id: uuid.UUID | None
    tenant_name: str | None = None
    full_name: str | None = None
    status: str
    created_at: datetime


class PasswordResetResult(BaseModel):
    """Resultado de un reset: la contraseña nueva se muestra UNA sola vez."""
    user_email: str
    new_password: str
