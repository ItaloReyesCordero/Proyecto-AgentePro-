"""Tests unitarios de app/utils/encryption.py (Fernet sobre SECRET_KEY)."""
from __future__ import annotations

import pytest

from app.utils.encryption import (
    decrypt,
    decrypt_if_value,
    encrypt,
    encrypt_if_value,
)


@pytest.mark.parametrize(
    "plain",
    [
        "EAAG...token-de-whatsapp",
        "hola mundo",
        "1234567890",
        "símbolos: ñ á é í ó ú",
        "x" * 4000,
        "con\nsaltos\nde linea",
        "{\"json\": true, \"n\": 1}",
    ],
)
def test_encrypt_decrypt_roundtrip(plain):
    cipher = encrypt(plain)
    assert cipher != plain
    assert decrypt(cipher) == plain


def test_encrypt_empty_returns_empty():
    assert encrypt("") == ""


def test_decrypt_empty_returns_empty():
    assert decrypt("") == ""


def test_encrypt_is_non_deterministic():
    # Fernet incluye un timestamp/IV: dos cifrados del mismo texto difieren...
    a, b = encrypt("igual"), encrypt("igual")
    assert a != b
    # ...pero ambos descifran al mismo claro.
    assert decrypt(a) == decrypt(b) == "igual"


def test_encrypt_if_value_none():
    assert encrypt_if_value(None) is None


def test_encrypt_if_value_real():
    assert decrypt(encrypt_if_value("secreto")) == "secreto"


def test_decrypt_if_value_none():
    assert decrypt_if_value(None) is None


def test_decrypt_if_value_invalid_returns_input():
    # Si el texto no es un token Fernet válido, devuelve el valor tal cual
    # (tolera datos no cifrados guardados antes).
    assert decrypt_if_value("texto-plano-no-cifrado") == "texto-plano-no-cifrado"


def test_decrypt_if_value_valid_roundtrip():
    assert decrypt_if_value(encrypt("abc")) == "abc"


@pytest.mark.parametrize("token", ["EAAG123", "" + "a" * 50, "phone-id-99"])
def test_encrypt_if_value_roundtrip(token):
    assert decrypt_if_value(encrypt_if_value(token)) == token
