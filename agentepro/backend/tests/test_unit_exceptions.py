"""Tests unitarios de las excepciones de dominio (status + code)."""
from __future__ import annotations

import pytest

from app.core.exceptions import (
    AgentProException,
    ContactNotFoundError,
    ConversationNotFoundError,
    DuplicateWebhookError,
    ExternalServiceError,
    NotFoundError,
    PaymentOverdueError,
    PlanLimitExceededError,
    ProvisioningError,
    TenantNotFoundError,
    TrialExpiredError,
    UnauthorizedError,
    ValidationError,
    WebhookVerificationError,
)


def test_base_exception_defaults():
    exc = AgentProException("algo")
    assert exc.status_code == 400
    assert exc.code == "INTERNAL_ERROR"
    assert str(exc) == "algo"


@pytest.mark.parametrize(
    "factory,status_code,code",
    [
        (lambda: TenantNotFoundError("slug"), 404, "TENANT_NOT_FOUND"),
        (lambda: UnauthorizedError(), 401, "UNAUTHORIZED"),
        (lambda: PlanLimitExceededError("messages"), 429, "PLAN_LIMIT_EXCEEDED"),
        (lambda: TrialExpiredError(), 402, "TRIAL_EXPIRED"),
        (lambda: PaymentOverdueError(), 402, "PAYMENT_OVERDUE"),
        (lambda: ProvisioningError("x"), 500, "PROVISIONING_ERROR"),
        (lambda: NotFoundError("Recurso"), 404, "NOT_FOUND"),
        (lambda: ContactNotFoundError("cid"), 404, "CONTACT_NOT_FOUND"),
        (lambda: ConversationNotFoundError("convid"), 404, "CONVERSATION_NOT_FOUND"),
        (lambda: DuplicateWebhookError("mid"), 409, "DUPLICATE_WEBHOOK"),
        (lambda: ValidationError("malo"), 422, "VALIDATION_ERROR"),
        (lambda: ExternalServiceError("Meta", "timeout"), 502, "EXTERNAL_SERVICE_ERROR"),
        (lambda: WebhookVerificationError(), 403, "WEBHOOK_VERIFICATION_FAILED"),
    ],
)
def test_exception_status_and_code(factory, status_code, code):
    exc = factory()
    assert isinstance(exc, AgentProException)
    assert exc.status_code == status_code
    assert exc.code == code
    assert exc.message  # tiene mensaje no vacío


def test_trial_expired_message_is_spanish():
    assert "prueba" in TrialExpiredError().message.lower()


def test_payment_overdue_message_mentions_pago():
    assert "pago" in PaymentOverdueError().message.lower()


def test_plan_limit_keeps_resource():
    assert PlanLimitExceededError("calls").resource == "calls"


def test_external_service_keeps_service_name():
    assert ExternalServiceError("Twilio", "boom").service == "Twilio"


def test_tenant_not_found_includes_slug_in_message():
    assert "mi-slug" in TenantNotFoundError("mi-slug").message


def test_validation_error_message_passthrough():
    assert ValidationError("campo inválido").message == "campo inválido"
