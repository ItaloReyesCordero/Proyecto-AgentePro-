from __future__ import annotations
import hmac
import hashlib
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import settings


class AgentProException(Exception):
    """Excepción base de AgentePro."""

    def __init__(self, message: str, status_code: int = 400, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class TenantNotFoundError(AgentProException):
    """Tenant no encontrado."""

    def __init__(self, slug: str = "") -> None:
        super().__init__(
            message=f"Tenant '{slug}' not found",
            status_code=404,
            code="TENANT_NOT_FOUND",
        )


class UnauthorizedError(AgentProException):
    """Acceso no autorizado."""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(message=detail, status_code=401, code="UNAUTHORIZED")


class PlanLimitExceededError(AgentProException):
    """Se lanza cuando se supera el límite del plan."""

    def __init__(self, resource: str = "messages") -> None:
        super().__init__(
            message=f"Plan limit exceeded for {resource}",
            status_code=429,
            code="PLAN_LIMIT_EXCEEDED",
        )
        self.resource = resource


class FeatureNotInPlanError(AgentProException):
    """El módulo solicitado no está incluido en el plan del negocio.

    Código 402 (no 403) para que el interceptor del frontend lo trate como un
    "mejora tu plan" y muestre la pantalla de upgrade, en vez de un error suelto.
    """

    def __init__(self, feature: str = "") -> None:
        super().__init__(
            message="Este módulo no está incluido en tu plan. Mejora tu plan para activarlo.",
            status_code=402,
            code="FEATURE_LOCKED",
        )
        self.feature = feature


class TrialExpiredError(AgentProException):
    """El período de prueba del tenant venció; debe actualizar su plan."""

    def __init__(self) -> None:
        super().__init__(
            message="Tu período de prueba terminó. Actualiza tu plan para continuar.",
            status_code=402,
            code="TRIAL_EXPIRED",
        )


class PaymentOverdueError(AgentProException):
    """El negocio fue suspendido por falta de pago; debe regularizar para continuar."""

    def __init__(self) -> None:
        super().__init__(
            message="Tu servicio está suspendido por falta de pago. Regulariza tu pago para reactivarlo.",
            status_code=402,
            code="PAYMENT_OVERDUE",
        )


class AccountSuspendedError(AgentProException):
    """El administrador desactivó la cuenta del negocio (is_active=False).

    Se usa código 402 (no 403) para que el frontend lo trate igual que una
    suspensión por pago: el interceptor redirige a la pantalla de contacto/pago
    en lugar de dejar al dueño con un dashboard a medias y errores sueltos.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Tu cuenta fue suspendida por el administrador. Contáctanos para reactivarla.",
            status_code=402,
            code="ACCOUNT_SUSPENDED",
        )


class ProvisioningError(AgentProException):
    """Error durante el aprovisionamiento de un tenant."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"Provisioning failed: {message}",
            status_code=500,
            code="PROVISIONING_ERROR",
        )


class NotFoundError(AgentProException):
    """Recurso no encontrado."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            code="NOT_FOUND",
        )


class ContactNotFoundError(AgentProException):
    """Contacto no encontrado."""

    def __init__(self, contact_id: str = "") -> None:
        super().__init__(
            message=f"Contact '{contact_id}' not found",
            status_code=404,
            code="CONTACT_NOT_FOUND",
        )


class ConversationNotFoundError(AgentProException):
    """Conversación no encontrada."""

    def __init__(self, conversation_id: str = "") -> None:
        super().__init__(
            message=f"Conversation '{conversation_id}' not found",
            status_code=404,
            code="CONVERSATION_NOT_FOUND",
        )


class DuplicateWebhookError(AgentProException):
    """Evento webhook duplicado."""

    def __init__(self, message_id: str = "") -> None:
        super().__init__(
            message=f"Duplicate webhook event: {message_id}",
            status_code=409,
            code="DUPLICATE_WEBHOOK",
        )


class ValidationError(AgentProException):
    """Error de validación."""

    def __init__(self, detail: str) -> None:
        super().__init__(message=detail, status_code=422, code="VALIDATION_ERROR")


class ExternalServiceError(AgentProException):
    """Error en servicio externo (Meta, Retell, Twilio, etc)."""

    def __init__(self, service: str, detail: str) -> None:
        super().__init__(
            message=f"Error in service {service}: {detail}",
            status_code=502,
            code="EXTERNAL_SERVICE_ERROR",
        )
        self.service = service


class WebhookVerificationError(AgentProException):
    """Error al verificar firma del webhook."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid webhook signature",
            status_code=403,
            code="WEBHOOK_VERIFICATION_FAILED",
        )


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AgentProException)
    async def agentpro_exception_handler(
        request: Request, exc: AgentProException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error": type(exc).__name__, "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": "InternalServerError"},
        )
