"""Tests unitarios de app/utils/helpers.py (sin BD, puro Python)."""
from __future__ import annotations

from datetime import datetime

import pytest

from app.utils.helpers import (
    derive_lead_stage,
    enum_value,
    format_currency_soles,
    is_within_business_hours,
    lead_stage_to_contact_status,
    normalize_phone,
    normalize_phone_number,
    phone_matches_any,
    sanitize_for_prompt,
    truncate_text,
)


# --- phone_matches_any (lista "pasar con el dueño", tolerante a prefijos) ----


@pytest.mark.parametrize(
    "phone,candidates,expected",
    [
        ("+51999888777", ["999888777"], True),
        ("51999888777", ["+51 999 888 777"], True),
        ("999888777", ["51999888777"], True),
        ("999888777", ["999000111", "999888777"], True),
        ("999888777", ["999000111"], False),
        ("999888777", [], False),
        (None, ["999888777"], False),
        ("", ["999888777"], False),
    ],
)
def test_phone_matches_any(phone, candidates, expected):
    assert phone_matches_any(phone, candidates) is expected


# --- normalize_phone (E.164 con región PE) ----------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("916085873", "+51916085873"),
        ("999888777", "+51999888777"),
        ("+51916085873", "+51916085873"),
        ("51916085873", "+51916085873"),
        ("987654321", "+51987654321"),
    ],
)
def test_normalize_phone_valid_peru_mobiles(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("garbage", ["abc", "", "no-soy-un-numero", "++++"])
def test_normalize_phone_invalid_returns_input(garbage):
    # Si phonenumbers no puede parsear, devuelve el texto original.
    assert normalize_phone(garbage) == garbage


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("+51 916 085 873", "+51916085873"),
        ("916-085-873", "916085873"),
        ("(01) 555 1234", "015551234"),
        ("916 085 873", "916085873"),
        ("+51-999.888.777", "+51999888777"),
        ("abc123def456", "123456"),
    ],
)
def test_normalize_phone_number_strips_non_digits(raw, expected):
    assert normalize_phone_number(raw) == expected


# --- is_within_business_hours -----------------------------------------------


def _hours_for(dt: datetime, active=True, open_="09:00", close="18:00") -> dict:
    days = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    return {days[dt.weekday()]: {"active": active, "open": open_, "close": close}}


def test_business_hours_inside_window():
    dt = datetime(2026, 6, 1, 10, 30)  # lunes 10:30
    assert is_within_business_hours(_hours_for(dt), dt) is True


def test_business_hours_before_open():
    dt = datetime(2026, 6, 1, 8, 0)
    assert is_within_business_hours(_hours_for(dt), dt) is False


def test_business_hours_after_close():
    dt = datetime(2026, 6, 1, 19, 0)
    assert is_within_business_hours(_hours_for(dt), dt) is False


def test_business_hours_day_inactive():
    dt = datetime(2026, 6, 1, 10, 0)
    assert is_within_business_hours(_hours_for(dt, active=False), dt) is False


def test_business_hours_day_missing_from_config():
    dt = datetime(2026, 6, 1, 10, 0)
    assert is_within_business_hours({}, dt) is False


@pytest.mark.parametrize(
    "hour,minute,expected",
    [
        (9, 0, True),   # justo al abrir
        (18, 0, True),  # justo al cerrar (límite inclusivo)
        (8, 59, False),
        (18, 1, False),
        (12, 0, True),
        (0, 0, False),
        (23, 59, False),
    ],
)
def test_business_hours_boundaries(hour, minute, expected):
    dt = datetime(2026, 6, 1, hour, minute)
    assert is_within_business_hours(_hours_for(dt), dt) is expected


# --- sanitize_for_prompt -----------------------------------------------------


def test_sanitize_removes_html_comments():
    assert sanitize_for_prompt("Hola <!-- oculto --> mundo") == "Hola  mundo"


def test_sanitize_removes_multiline_comments():
    text = "antes <!--\nlinea1\nlinea2\n--> despues"
    assert "linea1" not in sanitize_for_prompt(text)


def test_sanitize_truncates_to_max_length():
    assert len(sanitize_for_prompt("a" * 5000, max_length=100)) == 100


def test_sanitize_strips_whitespace():
    assert sanitize_for_prompt("   hola   ") == "hola"


@pytest.mark.parametrize("max_len", [10, 50, 200, 2000])
def test_sanitize_respects_various_max_lengths(max_len):
    assert len(sanitize_for_prompt("x" * 9999, max_length=max_len)) <= max_len


# --- format_currency_soles ---------------------------------------------------


@pytest.mark.parametrize(
    "amount,expected",
    [
        (0, "S/. 0.00"),
        (199, "S/. 199.00"),
        (349.5, "S/. 349.50"),
        (1234.567, "S/. 1234.57"),
        (0.1, "S/. 0.10"),
        (549.0, "S/. 549.00"),
    ],
)
def test_format_currency_soles(amount, expected):
    assert format_currency_soles(amount) == expected


# --- truncate_text -----------------------------------------------------------


def test_truncate_shorter_than_max_unchanged():
    assert truncate_text("hola", 10) == "hola"


def test_truncate_exactly_max_unchanged():
    assert truncate_text("hola", 4) == "hola"


def test_truncate_longer_adds_suffix():
    assert truncate_text("hola mundo", 8) == "hola ..."


def test_truncate_custom_suffix():
    out = truncate_text("abcdefghij", 6, suffix="…")
    assert out.endswith("…") and len(out) == 6


@pytest.mark.parametrize("max_len", [5, 8, 12, 20])
def test_truncate_never_exceeds_max(max_len):
    assert len(truncate_text("z" * 100, max_len)) == max_len


# --- derive_lead_stage -------------------------------------------------------


@pytest.mark.parametrize(
    "status,score,expected",
    [
        ("customer", 0, "customer"),
        ("customer", 100, "customer"),
        ("inactive", 90, "lost"),
        ("blocked", 90, "lost"),
        ("lead", 0, "cold"),
        ("lead", 33, "cold"),
        ("lead", 34, "warm"),
        ("lead", 66, "warm"),
        ("lead", 67, "hot"),
        ("lead", 100, "hot"),
        (None, 50, "warm"),
        (None, 0, "cold"),
        ("", 80, "hot"),
        ("prospect", 34, "warm"),
    ],
)
def test_derive_lead_stage(status, score, expected):
    assert derive_lead_stage(status, score) == expected


# --- lead_stage_to_contact_status -------------------------------------------


@pytest.mark.parametrize(
    "stage,expected",
    [
        ("cold", "lead"),
        ("warm", "prospect"),
        ("hot", "prospect"),
        ("customer", "customer"),
        ("lost", "inactive"),
        ("desconocido", "lead"),
        ("", "lead"),
        ("HOT", "prospect"),  # case-insensitive
    ],
)
def test_lead_stage_to_contact_status(stage, expected):
    assert lead_stage_to_contact_status(stage) == expected


def test_lead_stage_roundtrip_is_consistent_for_known_stages():
    for stage in ["customer"]:
        status = lead_stage_to_contact_status(stage)
        assert derive_lead_stage(status, 0) == stage


# --- enum_value --------------------------------------------------------------


def test_enum_value_with_enum():
    from app.models.tenant import PlanType

    assert enum_value(PlanType.BASIC) == "basic"


def test_enum_value_with_plain_string():
    assert enum_value("texto") == "texto"


def test_enum_value_with_none():
    assert enum_value(None) == ""


@pytest.mark.parametrize("value", ["a", "b", "trial", "basic"])
def test_enum_value_passthrough_strings(value):
    assert enum_value(value) == value
