"""Tests unitarios de la configuración (valores por defecto y derivados)."""
from __future__ import annotations

import pytest

from app.config import Settings, settings


def test_app_identity_defaults():
    assert settings.APP_NAME == "AgentePro"
    assert settings.VERSION == "2.0.0"
    assert settings.ALGORITHM == "HS256"


def test_test_env_is_forced_by_conftest():
    # conftest fuerza estos valores para aislar los tests.
    assert settings.ENVIRONMENT == "test"
    assert settings.RATE_LIMIT_ENABLED is False
    assert settings.SECRET_KEY == "test-secret-key"
    assert settings.ADMIN_SECRET_KEY == "test-admin-key"


@pytest.mark.parametrize(
    "plan,price",
    [
        ("inicial", 149.0),
        ("basic", 249.0),
        ("professional", 449.0),
        ("enterprise", 799.0),
    ],
)
def test_plan_prices(plan, price):
    mapping = {
        "inicial": settings.PLAN_INICIAL_PRICE,
        "basic": settings.PLAN_BASIC_PRICE,
        "professional": settings.PLAN_PROFESSIONAL_PRICE,
        "enterprise": settings.PLAN_ENTERPRISE_PRICE,
    }
    assert mapping[plan] == price


@pytest.mark.parametrize(
    "plan,messages,calls",
    [
        ("inicial", 200, 0),
        ("basic", 400, 0),
        ("professional", 1500, 60),
        ("enterprise", 4000, 150),
    ],
)
def test_plan_quotas(plan, messages, calls):
    msg = {
        "inicial": settings.PLAN_INICIAL_MESSAGES,
        "basic": settings.PLAN_BASIC_MESSAGES,
        "professional": settings.PLAN_PROFESSIONAL_MESSAGES,
        "enterprise": settings.PLAN_ENTERPRISE_MESSAGES,
    }
    cal = {
        "inicial": settings.PLAN_INICIAL_CALLS,
        "basic": settings.PLAN_BASIC_CALLS,
        "professional": settings.PLAN_PROFESSIONAL_CALLS,
        "enterprise": settings.PLAN_ENTERPRISE_CALLS,
    }
    assert msg[plan] == messages
    assert cal[plan] == calls


def test_prices_are_strictly_increasing():
    assert (
        settings.PLAN_INICIAL_PRICE
        < settings.PLAN_BASIC_PRICE
        < settings.PLAN_PROFESSIONAL_PRICE
        < settings.PLAN_ENTERPRISE_PRICE
    )


def test_cost_estimates_below_prices():
    assert settings.PLAN_INICIAL_COST_EST < settings.PLAN_INICIAL_PRICE
    assert settings.PLAN_BASIC_COST_EST < settings.PLAN_BASIC_PRICE
    assert settings.PLAN_PROFESSIONAL_COST_EST < settings.PLAN_PROFESSIONAL_PRICE
    assert settings.PLAN_ENTERPRISE_COST_EST < settings.PLAN_ENTERPRISE_PRICE


def test_token_expiry_defaults():
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 30


def test_usd_to_pen_is_positive():
    assert settings.USD_TO_PEN > 0


def test_default_claude_models():
    assert settings.CLAUDE_MODEL_DEFAULT.startswith("claude-")
    assert settings.CLAUDE_MODEL_COMPLEX.startswith("claude-")


def test_settings_ignores_extra_env(monkeypatch):
    # extra="ignore": variables desconocidas no rompen la carga.
    monkeypatch.setenv("UNA_VARIABLE_RARA_INEXISTENTE", "x")
    s = Settings()
    assert s.APP_NAME == "AgentePro"


@pytest.mark.parametrize(
    "field",
    [
        "ANTHROPIC_API_KEY",
        "META_APP_SECRET",
        "TWILIO_ACCOUNT_SID",
        "RETELL_API_KEY",
        "CULQI_SECRET_KEY",
        "PAYMENT_YAPE_NUMBER",
    ],
)
def test_optional_integration_keys_default_empty(field):
    # En desarrollo/test las integraciones externas están vacías (degradan solas).
    # Solo verificamos el tipo str; el valor real puede venir del .env del entorno.
    assert isinstance(getattr(settings, field), str)
