from __future__ import annotations

from app.core.rate_limit import FixedWindowLimiter
from app.core.security import (
    generate_temp_password,
    hash_password,
    verify_password,
)

# --- generate_temp_password -------------------------------------------------

_AMBIGUOUS = set("0O1lI")


def test_temp_password_length_and_charset() -> None:
    pw = generate_temp_password()
    assert len(pw) >= 12
    assert pw.isalnum()
    # No debe contener caracteres ambiguos (0/O, 1/l/I).
    assert not (set(pw) & _AMBIGUOUS)


def test_temp_password_is_random() -> None:
    passwords = {generate_temp_password() for _ in range(50)}
    assert len(passwords) == 50  # extremadamente improbable que colisionen


def test_temp_password_respects_min_length() -> None:
    # Aunque se pida menos de 8, se fuerza un mínimo seguro.
    assert len(generate_temp_password(4)) >= 8


def test_temp_password_hash_roundtrip() -> None:
    pw = generate_temp_password()
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("otra-cosa", hashed) is False


# --- FixedWindowLimiter -----------------------------------------------------


def test_limiter_allows_up_to_max_then_blocks() -> None:
    limiter = FixedWindowLimiter(max_hits=3, window_seconds=60)
    # Tiempo "congelado" en t=0 para no depender del reloj real.
    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=0.0) is False  # 4º intento bloqueado


def test_limiter_resets_after_window() -> None:
    limiter = FixedWindowLimiter(max_hits=2, window_seconds=60)
    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=30.0) is False  # misma ventana
    assert limiter.allow("ip", now=61.0) is True   # ventana nueva


def test_limiter_is_per_key() -> None:
    limiter = FixedWindowLimiter(max_hits=1, window_seconds=60)
    assert limiter.allow("ip-a", now=0.0) is True
    assert limiter.allow("ip-a", now=0.0) is False
    # Otra IP no se ve afectada por el límite de la primera.
    assert limiter.allow("ip-b", now=0.0) is True
