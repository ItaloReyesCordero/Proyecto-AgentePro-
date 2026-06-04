"""Aislamiento multi-tenant forzado a nivel de la capa de datos (RLS de aplicación).

Idea: cada `AsyncSession` de una petición autenticada lleva su `tenant_id` en
`session.info["tenant_id"]`. Un listener global de SQLAlchemy (`do_orm_execute`)
inyecta automáticamente `WHERE tenant_id = :tid` en TODAS las consultas SELECT de
las tablas con dueño (incluidas cargas por relación y joins). Así, aunque un
endpoint olvide filtrar, es **imposible** leer datos de otro negocio.

Cuando `session.info` no tiene `tenant_id` (procesos del sistema: login, webhooks,
panel de Super Admin, workers) no se aplica filtro — esos flujos resuelven el
tenant explícitamente y no deben quedar restringidos.

Esto es el complemento de aplicación al RLS nativo de Postgres (que se activa en
el despliegue de producción con un rol de BD restringido).
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

from app.models.agent_config import AgentConfig
from app.models.appointment import Appointment
from app.models.automation import Automation
from app.models.automation_run import AutomationRun
from app.models.call import Call
from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.hubspot_sync_log import HubspotSyncLog
from app.models.instagram_post import InstagramPost
from app.models.message import Message
from app.models.subscription import Subscription
from app.models.user import User
from app.models.voice_config import VoiceConfig
from app.models.webhook_log import WebhookLog

# Modelos con columna `tenant_id` que deben aislarse por negocio.
# (No se incluye `Tenant` —no tiene tenant_id, es el negocio en sí—.)
TENANT_MODELS = (
    User,
    Contact,
    Conversation,
    Message,
    Call,
    AgentConfig,
    VoiceConfig,
    Appointment,
    Automation,
    AutomationRun,
    InstagramPost,
    Subscription,
    HubspotSyncLog,
    WebhookLog,
)

_SESSION_KEY = "tenant_id"


def set_session_tenant(session, tenant_id) -> None:
    """Marca la sesión para que todas sus consultas se filtren por este tenant."""
    session.sync_session.info[_SESSION_KEY] = tenant_id


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_filter(execute_state) -> None:
    if not execute_state.is_select:
        return
    tid = execute_state.session.info.get(_SESSION_KEY)
    if tid is None:
        return
    execute_state.statement = execute_state.statement.options(
        *[
            with_loader_criteria(model, model.tenant_id == tid, include_aliases=True)
            for model in TENANT_MODELS
        ]
    )
