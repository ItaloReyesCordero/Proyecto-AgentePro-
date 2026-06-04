from __future__ import annotations
import base64
import hashlib
from cryptography.fernet import Fernet
from app.config import settings


def _get_fernet() -> Fernet:
    # Deriva una clave de 32 bytes del SECRET_KEY
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt(text: str) -> str:
    if not text:
        return text
    f = _get_fernet()
    return f.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    if not text:
        return text
    f = _get_fernet()
    return f.decrypt(text.encode()).decode()


def encrypt_if_value(value: str | None) -> str | None:
    if value is None:
        return None
    return encrypt(value)


def decrypt_if_value(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return decrypt(value)
    except Exception:
        return value
