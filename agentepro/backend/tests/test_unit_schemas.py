"""Tests unitarios de validación de schemas Pydantic (contratos de la API)."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.agent_config import AgentConfigUpdate
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.contact import ContactUpdate
from app.schemas.tenant import (
    ConfirmPaymentRequest,
    ProvisionRequest,
    TenantUpdate,
)


# --- auth --------------------------------------------------------------------


def test_register_request_defaults_business_type():
    req = RegisterRequest(
        email="a@example.com", password="x", full_name="N", business_name="B"
    )
    assert req.business_type == "other"


@pytest.mark.parametrize("email", ["no-arroba", "sin@dominio", "@example.com", ""])
def test_login_request_rejects_bad_email(email):
    with pytest.raises(ValidationError):
        LoginRequest(email=email, password="x")


def test_login_request_accepts_valid_email():
    assert LoginRequest(email="ok@example.com", password="x").email == "ok@example.com"


def test_register_requires_all_core_fields():
    with pytest.raises(ValidationError):
        RegisterRequest(email="a@example.com", password="x")  # faltan full_name/business_name


def test_change_password_request_fields():
    req = ChangePasswordRequest(current_password="a", new_password="b")
    assert req.current_password == "a" and req.new_password == "b"


# --- common ------------------------------------------------------------------


def test_message_response_defaults():
    m = MessageResponse()
    assert m.success is True
    assert m.message == "OK"


@pytest.mark.parametrize(
    "total,per_page,expected_pages",
    [(0, 20, 0), (1, 20, 1), (20, 20, 1), (21, 20, 2), (5, 2, 3), (100, 10, 10)],
)
def test_paginated_build_computes_pages(total, per_page, expected_pages):
    p = PaginatedResponse.build(items=[], total=total, page=1, per_page=per_page)
    assert p.pages == expected_pages
    assert p.total == total
    assert p.per_page == per_page


def test_paginated_build_with_zero_per_page():
    p = PaginatedResponse.build(items=[], total=10, page=1, per_page=0)
    assert p.pages == 0


# --- tenant ------------------------------------------------------------------


def test_confirm_payment_request_all_optional():
    req = ConfirmPaymentRequest()
    assert req.plan is None
    assert req.amount_pen is None


def test_confirm_payment_request_with_values():
    req = ConfirmPaymentRequest(plan="basic", amount_pen=199)
    assert req.plan == "basic"
    assert req.amount_pen == 199


def test_tenant_update_all_optional():
    assert TenantUpdate().model_dump(exclude_unset=True) == {}


def test_tenant_update_partial():
    assert TenantUpdate(name="X").model_dump(exclude_unset=True) == {"name": "X"}


def test_provision_request_requires_owner_email():
    with pytest.raises(ValidationError):
        ProvisionRequest(business_name="B", owner_name="O", owner_phone="9", owner_email="malo")


def test_provision_request_defaults():
    req = ProvisionRequest(
        business_name="B", owner_name="O", owner_phone="9", owner_email="o@example.com"
    )
    assert req.plan == "basic"
    assert req.business_type == "other"
    assert req.culqi_token is None


# --- agent / contact updates -------------------------------------------------


def test_agent_config_update_all_optional():
    assert AgentConfigUpdate().model_dump(exclude_unset=True) == {}


def test_agent_config_update_partial_temperature():
    dumped = AgentConfigUpdate(temperature=0.5).model_dump(exclude_unset=True)
    assert dumped == {"temperature": 0.5}


def test_contact_update_all_optional():
    assert ContactUpdate().model_dump(exclude_unset=True) == {}


def test_contact_update_tags_list():
    assert ContactUpdate(tags=["a", "b"]).tags == ["a", "b"]


@pytest.mark.parametrize("amount", [0, 199, 349, 549, 1000])
def test_confirm_payment_amount_accepts_ints(amount):
    assert ConfirmPaymentRequest(amount_pen=amount).amount_pen == amount
