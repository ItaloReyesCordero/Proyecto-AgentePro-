from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ProvisioningError
from app.core.plans import FEATURE_VOICE, plan_has_feature
from app.core.security import create_access_token, generate_webhook_verify_token, hash_password
from app.models.agent_config import AgentConfig
from app.models.automation import (
    Automation,
    AutomationStatus,
    AutomationTriggerType,
    AutomationType,
)
from app.models.tenant import BusinessType, PlanType, Tenant
from app.models.user import User, UserRole
from app.models.voice_config import VoiceConfig
from app.schemas.tenant import ProvisionRequest
from app.services.notification_service import send_welcome_email
from app.services.provisioning import (
    hubspot_provisioner,
    retell_provisioner,
    twilio_provisioner,
)
from app.utils.encryption import encrypt
from app.utils.logger import get_logger

logger = get_logger(__name__)

# FAQs por defecto según tipo de negocio.
_DEFAULT_FAQS: dict[str, list[dict[str, str]]] = {
    "healthcare": [
        {"question": "¿Cómo agendo una cita?", "answer": "Puedes agendar respondiendo este chat con la fecha y especialidad deseada.", "category": "citas"},
        {"question": "¿Qué especialidades atienden?", "answer": "Contamos con medicina general y especialidades. Cuéntame qué necesitas.", "category": "servicios"},
    ],
    "education": [
        {"question": "¿Cuánto cuesta la matrícula?", "answer": "Con gusto te comparto los precios. ¿Qué programa te interesa?", "category": "precios"},
        {"question": "¿Tienen modalidad virtual?", "answer": "Sí, ofrecemos modalidad presencial y virtual.", "category": "modalidad"},
    ],
    "retail": [
        {"question": "¿Hacen delivery?", "answer": "Sí, realizamos envíos. ¿A qué distrito?", "category": "delivery"},
        {"question": "¿Qué medios de pago aceptan?", "answer": "Aceptamos Yape, Plin, tarjetas y efectivo.", "category": "pagos"},
    ],
    "ecommerce": [
        {"question": "¿Cuánto demora el envío?", "answer": "Entre 24 y 72 horas según tu ubicación.", "category": "envios"},
        {"question": "¿Puedo cambiar un producto?", "answer": "Sí, tienes 7 días para cambios.", "category": "cambios"},
    ],
    "restaurant": [
        {"question": "¿Tienen delivery?", "answer": "Sí, pídenos por aquí y te lo llevamos.", "category": "delivery"},
        {"question": "¿Cuál es el horario?", "answer": "Atendemos según nuestro horario configurado.", "category": "horario"},
    ],
    "real_estate": [
        {"question": "¿Tienen propiedades disponibles?", "answer": "Sí, cuéntame qué zona y presupuesto buscas.", "category": "propiedades"},
    ],
    "services": [
        {"question": "¿Cuánto cuesta el servicio?", "answer": "Depende de tus necesidades, con gusto cotizamos.", "category": "precios"},
    ],
}


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{slug[:40]}-{secrets.token_hex(3)}"


def _plan_enum(plan: str) -> PlanType:
    try:
        return PlanType(plan)
    except ValueError:
        return PlanType.BASIC


def _business_enum(value: str) -> BusinessType:
    try:
        return BusinessType(value)
    except ValueError:
        return BusinessType.OTHER


class TenantProvisioner:
    """Orquesta el alta completa de un tenant con rollback ante fallos externos."""

    async def provision_new_tenant(
        self, data: ProvisionRequest, db: AsyncSession
    ) -> dict[str, object]:
        twilio_number: str | None = None
        retell_agent_id: str | None = None
        tenant_id = uuid.uuid4()

        try:
            slug = _slugify(data.business_name)
            business_type = _business_enum(data.business_type)
            plan = _plan_enum(data.plan)

            # Paso 1-2: Tenant + token de webhook
            tenant = Tenant(
                id=tenant_id,
                name=data.business_name,
                slug=slug,
                business_type=business_type,
                plan=plan,
                webhook_verify_token=generate_webhook_verify_token(slug),
                trial_ends_at=datetime.now(tz=timezone.utc) + timedelta(days=14),
            )
            db.add(tenant)
            await db.flush()

            # Usuario propietario: usa la contraseña elegida o una temporal
            temp_password = data.password or secrets.token_urlsafe(10)
            owner = User(
                tenant_id=tenant.id,
                email=str(data.owner_email),
                hashed_password=hash_password(temp_password),
                full_name=data.owner_name,
                role=UserRole.OWNER,
            )
            db.add(owner)

            # Paso 3: AgentConfig con defaults inteligentes
            agent_config = AgentConfig(
                tenant_id=tenant.id,
                agent_name="María",
                welcome_message=f"¡Hola! 👋 Soy María, asistente de {data.business_name}. ¿En qué puedo ayudarte?",
                faqs=_DEFAULT_FAQS.get(business_type.value, _DEFAULT_FAQS["services"]),
                escalation_phone=data.owner_phone,
                escalation_email=str(data.owner_email),
            )
            db.add(agent_config)

            voice_config = VoiceConfig(
                tenant_id=tenant.id,
                agent_name="María",
                voice_id=settings.RETELL_DEFAULT_VOICE_ID,
                escalation_phone=data.owner_phone,
            )
            db.add(voice_config)
            await db.flush()

            # Paso 4-7: VOZ (Twilio + Retell) — SOLO si el plan la incluye.
            # Inicial/Básico no tienen voz: así no gastamos en un número Twilio
            # ni creamos un agente Retell que no se usaría. El candado
            # `not tenant.retell_agent_id` evita duplicar la "María" si esto se
            # reejecutara para el mismo negocio (1 agente de voz por negocio).
            if plan_has_feature(plan, FEATURE_VOICE) and not tenant.retell_agent_id:
                # Twilio (compra + webhook de voz)
                twilio_number = twilio_provisioner.provision_phone_number(slug)
                tenant.twilio_phone_number = twilio_number

                # Retell (LLM + agente de voz). Le pasamos el webhook de nuestro
                # backend para que Retell registre las llamadas (inicio/fin/análisis).
                retell_webhook_url = (
                    f"{twilio_provisioner._backend_base()}/webhooks/retell/{slug}"
                )
                retell_agent_id, _llm_id = await retell_provisioner.provision_voice_agent(
                    voice_config, agent_config, webhook_url=retell_webhook_url
                )
                tenant.retell_agent_id = retell_agent_id
                voice_config.retell_agent_id = retell_agent_id

            # Paso 8: HubSpot company
            tenant.hubspot_company_id = await hubspot_provisioner.provision_hubspot_company(
                data.business_name
            )

            # Paso 9: Automatizaciones por defecto según plan
            self._create_default_automations(db, tenant, plan)

            # Paso 10: marcar como provisionado
            tenant.is_provisioned = True
            await db.flush()

            # Token de acceso para el dashboard
            access_token = create_access_token(
                {"sub": str(owner.id), "tenant_id": str(tenant.id)}
            )

            webhook_url = f"{twilio_provisioner._backend_base()}/webhooks/whatsapp/{slug}"
            dashboard_url = settings.FRONTEND_URL

            # Paso 11: email de bienvenida (best-effort)
            await send_welcome_email(
                to=str(data.owner_email),
                business_name=data.business_name,
                dashboard_url=dashboard_url,
                webhook_url=webhook_url,
                phone_number=twilio_number,
                temp_password=temp_password,
            )

            logger.info("tenant_provisioned", tenant_id=str(tenant.id), slug=slug)
            return {
                "tenant_id": tenant.id,
                "dashboard_url": dashboard_url,
                "webhook_url": webhook_url,
                "phone_number": twilio_number,
                "access_token": access_token,
            }

        except Exception as exc:
            logger.error("provisioning_failed", error=str(exc), tenant_id=str(tenant_id))
            # Rollback de servicios externos
            if twilio_number:
                twilio_provisioner.release_phone_number(twilio_number)
            if retell_agent_id:
                await retell_provisioner.rollback_voice_agent(retell_agent_id)
            await db.rollback()
            raise ProvisioningError(str(exc)) from exc

    def _create_default_automations(
        self, db: AsyncSession, tenant: Tenant, plan: PlanType
    ) -> None:
        automations: list[Automation] = [
            Automation(
                tenant_id=tenant.id,
                name="Seguimiento de leads por WhatsApp",
                description="Reactiva leads sin respuesta tras 24h.",
                automation_type=AutomationType.FOLLOW_UP,
                status=AutomationStatus.ACTIVE,
                trigger_type=AutomationTriggerType.SCHEDULED,
                trigger_config={"trigger": "no_response_hours", "value": 24},
            )
        ]
        if plan in (PlanType.PROFESSIONAL, PlanType.ENTERPRISE):
            automations.append(
                Automation(
                    tenant_id=tenant.id,
                    name="Reporte semanal",
                    description="Resumen semanal del negocio por WhatsApp.",
                    automation_type=AutomationType.BROADCAST,
                    status=AutomationStatus.ACTIVE,
                    trigger_type=AutomationTriggerType.SCHEDULED,
                    cron_expression="0 8 * * 1",
                )
            )
        if plan == PlanType.ENTERPRISE:
            automations.append(
                Automation(
                    tenant_id=tenant.id,
                    name="Reactivación de contactos inactivos",
                    description="Reengancha contactos sin actividad reciente.",
                    automation_type=AutomationType.REACTIVATION,
                    status=AutomationStatus.ACTIVE,
                    trigger_type=AutomationTriggerType.SCHEDULED,
                    trigger_config={"inactive_days": 30},
                )
            )
        for a in automations:
            db.add(a)
