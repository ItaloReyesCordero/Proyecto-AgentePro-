"""Tests unitarios de app/core/security.py (hashing, JWT, tokens)."""
from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_temp_password,
    generate_webhook_verify_token,
    get_password_hash,
    hash_password,
    verify_admin_key,
    verify_password,
)


# --- Password hashing --------------------------------------------------------


@pytest.mark.parametrize(
    "password",
    ["abc123", "Secret123", "S/.contraseña-larga!", "12345678", "áéíóú-ñ", "x" * 60],
)
def test_hash_and_verify_roundtrip(password):
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_verify_wrong_password_fails():
    hashed = hash_password("correcta")
    assert verify_password("incorrecta", hashed) is False


def test_hash_is_salted_unique_each_time():
    a = hash_password("misma")
    b = hash_password("misma")
    assert a != b  # bcrypt usa sal aleatoria
    assert verify_password("misma", a)
    assert verify_password("misma", b)


def test_get_password_hash_is_alias():
    assert get_password_hash is hash_password


def test_bcrypt_hash_has_expected_prefix():
    assert hash_password("hola").startswith("$2")


# --- JWT: access ------------------------------------------------------------


def test_access_token_roundtrip():
    token = create_access_token({"sub": "user-1", "tenant_id": "t-1"})
    payload = decode_token(token)
    assert payload["sub"] == "user-1"
    assert payload["tenant_id"] == "t-1"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_has_type_refresh():
    payload = decode_token(create_refresh_token({"sub": "u"}))
    assert payload["type"] == "refresh"


def test_access_and_refresh_have_different_types():
    a = decode_token(create_access_token({"sub": "u"}))
    r = decode_token(create_refresh_token({"sub": "u"}))
    assert a["type"] != r["type"]


def test_expired_token_raises_401():
    token = create_access_token({"sub": "u"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(HTTPException) as exc:
        decode_token(token)
    assert exc.value.status_code == 401


@pytest.mark.parametrize("bad", ["", "no.es.jwt", "abc", "a.b.c", "Bearer xxx"])
def test_decode_invalid_token_raises_401(bad):
    with pytest.raises(HTTPException) as exc:
        decode_token(bad)
    assert exc.value.status_code == 401


def test_tampered_token_raises():
    token = create_access_token({"sub": "u"})
    tampered = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    with pytest.raises(HTTPException):
        decode_token(tampered)


def test_token_preserves_custom_claims():
    token = create_access_token({"sub": "u", "role": "owner", "extra": 42})
    payload = decode_token(token)
    assert payload["role"] == "owner"
    assert payload["extra"] == 42


# --- generate_temp_password --------------------------------------------------


def test_temp_password_default_length():
    assert len(generate_temp_password()) == 12


@pytest.mark.parametrize("length,expected", [(8, 8), (16, 16), (20, 20), (4, 8), (1, 8)])
def test_temp_password_enforces_min_length(length, expected):
    # Longitudes menores a 8 se elevan a 8.
    assert len(generate_temp_password(length)) == expected


def test_temp_password_no_ambiguous_chars():
    pwd = "".join(generate_temp_password(20) for _ in range(50))
    for ch in "0O1lI":
        assert ch not in pwd


def test_temp_passwords_are_random():
    passwords = {generate_temp_password() for _ in range(50)}
    assert len(passwords) > 45  # casi todas distintas


def test_temp_password_only_allowed_alphabet():
    allowed = set("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789")
    assert set(generate_temp_password(40)) <= allowed


# --- verify_admin_key --------------------------------------------------------


def test_verify_admin_key_correct():
    # conftest fuerza ADMIN_SECRET_KEY="test-admin-key".
    assert verify_admin_key("test-admin-key") is True


@pytest.mark.parametrize("wrong", ["", "test-admin-key ", "TEST-ADMIN-KEY", "otro", "x"])
def test_verify_admin_key_wrong(wrong):
    assert verify_admin_key(wrong) is False


# --- generate_webhook_verify_token ------------------------------------------


def test_webhook_token_is_deterministic():
    assert generate_webhook_verify_token("mi-negocio") == generate_webhook_verify_token("mi-negocio")


def test_webhook_token_differs_per_slug():
    assert generate_webhook_verify_token("a") != generate_webhook_verify_token("b")


def test_webhook_token_length_is_32():
    assert len(generate_webhook_verify_token("cualquiera")) == 32


@pytest.mark.parametrize("slug", ["neg-1", "neg-2", "panaderia-xyz", "café-pe"])
def test_webhook_token_is_hex(slug):
    token = generate_webhook_verify_token(slug)
    int(token, 16)  # no lanza si es hex válido
