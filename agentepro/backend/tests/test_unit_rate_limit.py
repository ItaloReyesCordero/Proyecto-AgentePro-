"""Tests unitarios del limitador de ventana fija (fallback sin Redis)."""
from __future__ import annotations

import pytest

from app.core.rate_limit import FixedWindowLimiter


def test_allows_up_to_max_hits():
    limiter = FixedWindowLimiter(max_hits=3, window_seconds=60)
    assert limiter.allow("k", now=0.0) is True
    assert limiter.allow("k", now=1.0) is True
    assert limiter.allow("k", now=2.0) is True
    # El 4º acceso dentro de la ventana se rechaza.
    assert limiter.allow("k", now=3.0) is False


def test_window_resets_after_expiry():
    limiter = FixedWindowLimiter(max_hits=2, window_seconds=60)
    assert limiter.allow("k", now=0.0) is True
    assert limiter.allow("k", now=10.0) is True
    assert limiter.allow("k", now=20.0) is False
    # Pasada la ventana (>=60s desde el inicio) vuelve a permitir.
    assert limiter.allow("k", now=60.0) is True


def test_keys_are_independent():
    limiter = FixedWindowLimiter(max_hits=1, window_seconds=60)
    assert limiter.allow("ip-a", now=0.0) is True
    assert limiter.allow("ip-b", now=0.0) is True
    assert limiter.allow("ip-a", now=1.0) is False
    assert limiter.allow("ip-b", now=1.0) is False


def test_reset_clears_buckets():
    limiter = FixedWindowLimiter(max_hits=1, window_seconds=60)
    assert limiter.allow("k", now=0.0) is True
    assert limiter.allow("k", now=1.0) is False
    limiter.reset()
    assert limiter.allow("k", now=2.0) is True


@pytest.mark.parametrize("max_hits", [1, 5, 10, 100])
def test_exactly_max_hits_allowed(max_hits):
    limiter = FixedWindowLimiter(max_hits=max_hits, window_seconds=60)
    allowed = sum(1 for i in range(max_hits + 20) if limiter.allow("k", now=float(i) * 0.01))
    assert allowed == max_hits


@pytest.mark.parametrize("window", [1, 30, 60, 300])
def test_new_window_grants_fresh_quota(window):
    limiter = FixedWindowLimiter(max_hits=2, window_seconds=window)
    assert limiter.allow("k", now=0.0)
    assert limiter.allow("k", now=0.5)
    assert limiter.allow("k", now=0.9) is False
    assert limiter.allow("k", now=float(window)) is True


def test_default_now_uses_monotonic_clock():
    # Sin pasar `now` debe usar el reloj real y permitir el primer acceso.
    limiter = FixedWindowLimiter(max_hits=1, window_seconds=60)
    assert limiter.allow("real") is True
    assert limiter.allow("real") is False
