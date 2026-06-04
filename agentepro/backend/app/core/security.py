from __future__ import annotations
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash bcrypt de una contraseña."""
    return pwd_context.hash(password)


# Alias for backwards compatibility
hash_password = get_password_hash


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Crea un JWT de acceso con expiración corta."""
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Crea un JWT de refresco con expiración larga."""
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un JWT. Lanza HTTPException si inválido."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_temp_password(length: int = 12) -> str:
    """Genera una contraseña temporal al azar, legible (sin caracteres ambiguos
    como 0/O o l/1). Se usa cuando el super admin restablece la clave de un
    negocio: se le muestra UNA vez para que se la entregue al dueño."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"
    length = max(8, length)
    return "".join(secrets.choice(alphabet) for _ in range(length))


def verify_admin_key(admin_key: str) -> bool:
    """Verifica la clave de administración usando comparación segura."""
    return hmac.compare_digest(admin_key, settings.ADMIN_SECRET_KEY)


def generate_webhook_verify_token(tenant_slug: str) -> str:
    """Genera un token de verificación para webhooks Meta."""
    raw = f"{tenant_slug}:{settings.META_VERIFY_TOKEN_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]
