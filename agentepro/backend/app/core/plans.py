"""Definición central de planes: límites (mensajes/llamadas) y módulos habilitados.

Un solo lugar para responder dos preguntas:
  - ¿Cuántos mensajes/llamadas tiene este plan? -> `message_limit` / `call_limit`
  - ¿Qué módulos (features) puede usar este plan? -> `plan_features` / `plan_has_feature`

Así el bloqueo por plan no queda regado por el código. Los NÚMEROS viven en
`config.py` (ajustables sin tocar lógica); aquí vive el MAPA plan -> módulos.
"""
from __future__ import annotations

from app.config import settings
from app.models.tenant import PlanType

# --- Módulos (features) que se pueden bloquear por plan -----------------------
# Dashboard, Conversaciones, Agente IA y Configuración NO se gatean: todos los
# planes los tienen (son el mínimo para operar WhatsApp con IA).
FEATURE_CONTACTS = "contacts"
FEATURE_INSTAGRAM = "instagram"
FEATURE_APPOINTMENTS = "appointments"
FEATURE_VOICE = "voice"
FEATURE_AUTOMATIONS = "automations"

ALL_FEATURES = (
    FEATURE_CONTACTS,
    FEATURE_INSTAGRAM,
    FEATURE_APPOINTMENTS,
    FEATURE_VOICE,
    FEATURE_AUTOMATIONS,
)

# Mapa plan -> módulos habilitados.
_PLAN_FEATURES: dict[PlanType, set[str]] = {
    PlanType.INICIAL: set(),
    PlanType.BASIC: {FEATURE_CONTACTS},
    PlanType.PROFESSIONAL: {
        FEATURE_CONTACTS,
        FEATURE_INSTAGRAM,
        FEATURE_APPOINTMENTS,
        FEATURE_VOICE,
    },
    PlanType.ENTERPRISE: {
        FEATURE_CONTACTS,
        FEATURE_INSTAGRAM,
        FEATURE_APPOINTMENTS,
        FEATURE_VOICE,
        FEATURE_AUTOMATIONS,
    },
    # Trial: prueba TODO lo bueno de Profesional (para enamorar al cliente),
    # pero con topes de prueba muy bajos (ver _MESSAGE_LIMITS / _CALL_LIMITS).
    PlanType.TRIAL: {
        FEATURE_CONTACTS,
        FEATURE_INSTAGRAM,
        FEATURE_APPOINTMENTS,
        FEATURE_VOICE,
    },
}


def _coerce(plan: PlanType | str) -> PlanType:
    if isinstance(plan, PlanType):
        return plan
    try:
        return PlanType(str(plan))
    except ValueError:
        return PlanType.TRIAL


def plan_features(plan: PlanType | str) -> set[str]:
    """Conjunto de módulos habilitados para el plan."""
    return set(_PLAN_FEATURES.get(_coerce(plan), set()))


def plan_has_feature(plan: PlanType | str, feature: str) -> bool:
    """True si el plan incluye ese módulo."""
    return feature in plan_features(plan)


def _message_limits() -> dict[PlanType, int]:
    return {
        PlanType.INICIAL: settings.PLAN_INICIAL_MESSAGES,
        PlanType.BASIC: settings.PLAN_BASIC_MESSAGES,
        PlanType.PROFESSIONAL: settings.PLAN_PROFESSIONAL_MESSAGES,
        PlanType.ENTERPRISE: settings.PLAN_ENTERPRISE_MESSAGES,
        PlanType.TRIAL: settings.PLAN_TRIAL_MESSAGES,
    }


def _call_limits() -> dict[PlanType, int]:
    return {
        PlanType.INICIAL: settings.PLAN_INICIAL_CALLS,
        PlanType.BASIC: settings.PLAN_BASIC_CALLS,
        PlanType.PROFESSIONAL: settings.PLAN_PROFESSIONAL_CALLS,
        PlanType.ENTERPRISE: settings.PLAN_ENTERPRISE_CALLS,
        PlanType.TRIAL: settings.PLAN_TRIAL_CALLS,
    }


def message_limit(plan: PlanType | str) -> int:
    """Tope de mensajes IA/mes del plan."""
    return _message_limits().get(_coerce(plan), settings.PLAN_INICIAL_MESSAGES)


def call_limit(plan: PlanType | str) -> int:
    """Tope de llamadas de voz/mes del plan (0 = el plan no incluye voz)."""
    return _call_limits().get(_coerce(plan), 0)
