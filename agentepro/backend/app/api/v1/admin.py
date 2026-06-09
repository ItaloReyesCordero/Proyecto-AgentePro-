from __future__ import annotations

import calendar
import enum
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, func, inspect as sa_inspect, select, update

from app.config import settings
from app.core.security import generate_temp_password, hash_password
from app.dependencies import AdminGuard, DbSession
from app.models.agent_config import AgentConfig
from app.models.automation import Automation
from app.models.call import Call
from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.instagram_post import InstagramPost
from app.models.message import Message
from app.models.password_reset import PasswordResetRequest, ResetStatus
from app.models.tenant import PlanType, Tenant
from app.models.user import User, UserRole
from app.models.voice_config import VoiceConfig
from app.models.webhook_log import WebhookLog
from app.schemas.auth import PasswordResetRequestOut, PasswordResetResult
from app.schemas.common import MessageResponse
from app.schemas.tenant import (
    BillingPendingOut,
    ConfirmPaymentRequest,
    ProvisionRequest,
    TenantOut,
    TenantUpdate,
)
from app.services.provisioning.tenant_provisioner import TenantProvisioner

router = APIRouter(prefix="/admin", tags=["admin"])

_provisioner = TenantProvisioner()

# Columnas que nunca deben salir en un export (credenciales/secretos).
_SENSITIVE_COLUMNS = {
    "hashed_password",
    "whatsapp_access_token",
    "instagram_access_token",
    "webhook_verify_token",
    "notion_api_key",
}


def _serialize(obj: object) -> dict[str, object]:
    """Convierte una fila ORM a dict JSON-safe, omitiendo columnas sensibles."""
    data: dict[str, object] = {}
    for attr in sa_inspect(obj).mapper.column_attrs:
        key = attr.key
        if key in _SENSITIVE_COLUMNS:
            continue
        value = getattr(obj, key)
        if isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, enum.Enum):
            value = value.value
        data[key] = value
    return data


@router.post("/reset-usage", response_model=MessageResponse)
async def reset_monthly_usage(_: AdminGuard, db: DbSession) -> MessageResponse:
    """Reinicia los contadores de uso mensual de TODOS los tenants."""
    await db.execute(
        update(Tenant).values(messages_used_this_month=0, calls_used_this_month=0)
    )
    await db.flush()
    return MessageResponse(message="Uso mensual reiniciado para todos los tenants")


@router.get("/tenants", response_model=list[TenantOut])
async def list_tenants(_: AdminGuard, db: DbSession) -> list[TenantOut]:
    result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    return [TenantOut.from_model(t) for t in result.scalars().all()]


@router.get("/tenants/{tenant_id}", response_model=TenantOut)
async def get_tenant(tenant_id: uuid.UUID, _: AdminGuard, db: DbSession) -> TenantOut:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantOut.from_model(tenant)


@router.patch("/tenants/{tenant_id}", response_model=TenantOut)
async def update_tenant(
    tenant_id: uuid.UUID, payload: TenantUpdate, _: AdminGuard, db: DbSession
) -> TenantOut:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if payload.name is not None:
        tenant.name = payload.name
    if payload.is_active is not None:
        tenant.is_active = payload.is_active
    if payload.plan is not None:
        from app.models.tenant import PlanType

        try:
            tenant.plan = PlanType(payload.plan)
        except ValueError:
            pass
    await db.flush()
    return TenantOut.from_model(tenant)


@router.get("/metrics/global")
async def global_metrics(_: AdminGuard, db: DbSession) -> dict[str, int]:
    tenants = int((await db.execute(select(func.count(Tenant.id)))).scalar() or 0)
    active = int(
        (await db.execute(select(func.count(Tenant.id)).where(Tenant.is_active))).scalar() or 0
    )
    contacts = int((await db.execute(select(func.count(Contact.id)))).scalar() or 0)
    messages = int((await db.execute(select(func.count(Message.id)))).scalar() or 0)
    calls = int((await db.execute(select(func.count(Call.id)))).scalar() or 0)
    return {
        "total_tenants": tenants,
        "active_tenants": active,
        "total_contacts": contacts,
        "total_messages": messages,
        "total_calls": calls,
    }


@router.get("/analytics")
async def analytics(_: AdminGuard, db: DbSession) -> dict[str, object]:
    """Analítica de negocio para el panel del fundador: por cada tenant —uso real
    (contactos, mensajes, llamadas, tokens/costo Claude)— más economía (ingreso
    según plan, costo estimado y ganancia). Incluye totales y series mensuales.
    """
    prices = {
        "inicial": settings.PLAN_INICIAL_PRICE,
        "basic": settings.PLAN_BASIC_PRICE,
        "professional": settings.PLAN_PROFESSIONAL_PRICE,
        "enterprise": settings.PLAN_ENTERPRISE_PRICE,
        "trial": 0.0,
    }
    usd_to_pen = settings.USD_TO_PEN

    tenants = (await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))).scalars().all()

    contact_counts = dict(
        (await db.execute(select(Contact.tenant_id, func.count(Contact.id)).group_by(Contact.tenant_id))).all()
    )
    msg_rows = (
        await db.execute(
            select(
                Message.tenant_id,
                func.count(Message.id),
                func.coalesce(func.sum(Message.tokens_used), 0),
            ).group_by(Message.tenant_id)
        )
    ).all()
    msg_counts = {r[0]: int(r[1]) for r in msg_rows}
    token_sums = {r[0]: int(r[2]) for r in msg_rows}
    # Llamadas: conteo y SEGUNDOS reales por negocio (para el costo de voz real).
    call_rows = (
        await db.execute(
            select(
                Call.tenant_id,
                func.count(Call.id),
                func.coalesce(func.sum(Call.duration_seconds), 0),
            ).group_by(Call.tenant_id)
        )
    ).all()
    call_counts = {r[0]: int(r[1]) for r in call_rows}
    call_seconds = {r[0]: int(r[2]) for r in call_rows}
    # Conversaciones reales por negocio (para el costo real de WhatsApp/Meta).
    conv_counts = dict(
        (await db.execute(select(Conversation.tenant_id, func.count(Conversation.id)).group_by(Conversation.tenant_id))).all()
    )

    voice_usd_per_min = settings.RETELL_USD_PER_MIN + settings.TWILIO_USD_PER_MIN
    wa_usd_per_conv = settings.WHATSAPP_USD_PER_CONVERSATION

    per_tenant: list[dict[str, object]] = []
    mrr = 0.0
    profit_total = 0.0
    claude_usd_total = 0.0
    cost_pen_total = 0.0
    by_plan: dict[str, int] = {"inicial": 0, "basic": 0, "professional": 0, "enterprise": 0, "trial": 0}

    for t in tenants:
        plan = t.plan.value if hasattr(t.plan, "value") else str(t.plan)
        tokens = token_sums.get(t.id, 0)
        seconds = int(call_seconds.get(t.id, 0) or 0)
        convs = int(conv_counts.get(t.id, 0) or 0)
        # Costos REALES (medidos por consumo), en USD.
        claude_usd = round(tokens / 1_000_000 * settings.CLAUDE_USD_PER_MTOK, 2)
        voice_usd = round(seconds / 60 * voice_usd_per_min, 2)
        whatsapp_usd = round(convs * wa_usd_per_conv, 2)
        cost_usd = round(claude_usd + voice_usd + whatsapp_usd, 2)
        cost_pen = round(cost_usd * usd_to_pen, 2)
        revenue = prices.get(plan, 0.0)
        profit = round(revenue - cost_pen, 2)
        by_plan[plan] = by_plan.get(plan, 0) + 1
        claude_usd_total += claude_usd
        cost_pen_total += cost_pen
        if t.is_active and plan != "trial":
            mrr += revenue
        profit_total += profit  # ganancia real total (incluye costo de trials, que es real)
        per_tenant.append(
            {
                "id": str(t.id),
                "name": t.name,
                "plan": plan,
                "is_active": t.is_active,
                "contacts": int(contact_counts.get(t.id, 0) or 0),
                "messages": msg_counts.get(t.id, 0),
                "calls": int(call_counts.get(t.id, 0) or 0),
                "call_seconds": seconds,
                "conversations": convs,
                "tokens_used": tokens,
                "claude_usd": claude_usd,
                "voice_usd": voice_usd,
                "whatsapp_usd": whatsapp_usd,
                "cost_usd": cost_usd,
                "cost_pen": cost_pen,
                "revenue_pen": revenue,
                "profit_pen": profit,
            }
        )

    # Series mensuales (últimos 6 meses), agregadas en Python para ser portables.
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=183)
    months: dict[str, dict[str, float]] = {}

    def _bucket(dt: datetime) -> str:
        return dt.strftime("%Y-%m")

    msg_times = (
        await db.execute(
            select(Message.created_at, func.coalesce(Message.tokens_used, 0)).where(
                Message.created_at >= cutoff
            )
        )
    ).all()
    for created_at, tok in msg_times:
        if created_at is None:
            continue
        b = months.setdefault(_bucket(created_at), {"messages": 0, "calls": 0, "claude_usd": 0.0})
        b["messages"] += 1
        b["claude_usd"] += (int(tok or 0) / 1_000_000) * settings.CLAUDE_USD_PER_MTOK

    call_times = (
        await db.execute(select(Call.created_at).where(Call.created_at >= cutoff))
    ).all()
    for (created_at,) in call_times:
        if created_at is None:
            continue
        b = months.setdefault(_bucket(created_at), {"messages": 0, "calls": 0, "claude_usd": 0.0})
        b["calls"] += 1

    monthly = [
        {
            "month": k,
            "messages": int(v["messages"]),
            "calls": int(v["calls"]),
            "claude_usd": round(v["claude_usd"], 2),
        }
        for k, v in sorted(months.items())
    ]

    active_paid = sum(1 for t in tenants if t.is_active and (t.plan.value if hasattr(t.plan, "value") else str(t.plan)) != "trial")
    return {
        "totals": {
            "total_tenants": len(tenants),
            "active_paid_tenants": active_paid,
            "trial_tenants": by_plan.get("trial", 0),
            "mrr_pen": round(mrr, 2),
            "real_cost_pen_total": round(cost_pen_total, 2),
            "est_monthly_profit_pen": round(profit_total, 2),
            "claude_usd_total": round(claude_usd_total, 2),
            "total_messages": sum(msg_counts.values()),
            "total_calls": sum(int(v or 0) for v in call_counts.values()),
        },
        "by_plan": by_plan,
        "tenants": per_tenant,
        "monthly": monthly,
    }


@router.get("/costs/global")
async def global_costs(_: AdminGuard, db: DbSession) -> dict[str, float | int]:
    tokens = int(
        (await db.execute(select(func.coalesce(func.sum(Message.tokens_used), 0)))).scalar() or 0
    )
    calls = int((await db.execute(select(func.count(Call.id)))).scalar() or 0)
    claude_usd = round(tokens / 1_000_000 * settings.CLAUDE_USD_PER_MTOK, 2)
    return {"tokens_used": tokens, "calls_count": calls, "claude_usd_est": claude_usd}


@router.get("/health")
async def services_health(_: AdminGuard, db: DbSession) -> dict[str, bool]:
    # Instagram y Notion no usan una API key global del backend: cada negocio
    # conecta la suya (token cifrado en su tenant). Por eso aquí mostramos ✓ si
    # al menos un negocio las tiene conectadas, no una variable de entorno.
    instagram_connected = await db.scalar(
        select(func.count())
        .select_from(Tenant)
        .where(Tenant.instagram_access_token.isnot(None))
        .where(Tenant.instagram_access_token != "")
        .where(Tenant.instagram_account_id.isnot(None))
    )
    notion_connected = await db.scalar(
        select(func.count())
        .select_from(Tenant)
        .where(Tenant.notion_api_key.isnot(None))
        .where(Tenant.notion_api_key != "")
        .where(Tenant.notion_database_id.isnot(None))
    )
    return {
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
        "meta_whatsapp": bool(settings.META_APP_SECRET),
        "twilio": bool(settings.TWILIO_ACCOUNT_SID),
        "retell": bool(settings.RETELL_API_KEY),
        "hubspot": bool(settings.HUBSPOT_ACCESS_TOKEN),
        "culqi": bool(settings.CULQI_SECRET_KEY),
        "resend": bool(settings.RESEND_API_KEY),
        "fal": bool(settings.FAL_KEY),
        "instagram": bool(instagram_connected),
        "notion": bool(notion_connected),
    }


@router.post("/tenants/{tenant_id}/deactivate", response_model=MessageResponse)
async def deactivate_tenant(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> MessageResponse:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.is_active = False
    await db.flush()
    return MessageResponse(message="Tenant desactivado")


# ---------------------------------------------------------------------------
# Cobro manual (sin pasarela): el dueño confirma pagos recibidos por Yape/
# transferencia y suspende a quien no paga. Culqi queda inerte (degrada solo).
# ---------------------------------------------------------------------------

def _plan_price(plan: str) -> int:
    return {
        "inicial": int(settings.PLAN_INICIAL_PRICE),
        "basic": int(settings.PLAN_BASIC_PRICE),
        "professional": int(settings.PLAN_PROFESSIONAL_PRICE),
        "enterprise": int(settings.PLAN_ENTERPRISE_PRICE),
    }.get(plan, 0)


def _effective_amount(tenant: Tenant) -> int:
    if tenant.monthly_amount_pen:
        return tenant.monthly_amount_pen
    plan = tenant.plan.value if hasattr(tenant.plan, "value") else str(tenant.plan)
    return _plan_price(plan)


def _add_one_month(dt: datetime) -> datetime:
    """Suma un mes calendario, ajustando el día si el mes destino es más corto."""
    month = dt.month % 12 + 1
    year = dt.year + (1 if dt.month == 12 else 0)
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


@router.get("/billing/pending", response_model=list[BillingPendingOut])
async def billing_pending(_: AdminGuard, db: DbSession) -> list[BillingPendingOut]:
    """Negocios por cobrar: por vencer (≤3 días), vencidos o suspendidos por pago.
    Incluye trials a punto de expirar para que cobres la primera mensualidad."""
    now = datetime.now(tz=timezone.utc)
    tenants = (await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))).scalars().all()
    out: list[BillingPendingOut] = []
    for t in tenants:
        state = t.payment_state
        if state not in ("due_soon", "overdue", "suspended"):
            continue
        due = t.payment_due_at
        if due is not None and due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        days_overdue = int((now - due).total_seconds() // 86400) if due is not None else 0
        out.append(
            BillingPendingOut(
                id=t.id,
                name=t.name,
                plan=t.plan.value if hasattr(t.plan, "value") else str(t.plan),
                payment_state=state,
                due_at=due,
                days_overdue=days_overdue,
                amount_pen=_effective_amount(t),
                is_active=t.is_active,
            )
        )
    # Más urgente primero (vencidos/suspendidos arriba).
    out.sort(key=lambda r: r.days_overdue, reverse=True)
    return out


@router.post("/tenants/{tenant_id}/confirm-payment", response_model=TenantOut)
async def confirm_payment(
    tenant_id: uuid.UUID, payload: ConfirmPaymentRequest, _: AdminGuard, db: DbSession
) -> TenantOut:
    """Registra un pago recibido por adelantado: marca el mes como pagado, mueve el
    vencimiento un mes y reactiva el servicio si estaba suspendido. Si el negocio
    estaba en prueba, lo pasa a un plan pagado (por defecto 'basic')."""
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if payload.plan:
        try:
            tenant.plan = PlanType(payload.plan)
        except ValueError:
            raise HTTPException(status_code=422, detail="Plan inválido")
    if tenant.plan == PlanType.TRIAL:
        tenant.plan = PlanType.BASIC
    if payload.amount_pen is not None:
        tenant.monthly_amount_pen = payload.amount_pen

    now = datetime.now(tz=timezone.utc)
    # Pago anticipado: si aún no vence, se acumula sobre la fecha vigente.
    base = now
    if tenant.next_payment_due is not None:
        due = tenant.next_payment_due
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        if due > now:
            base = due
    tenant.next_payment_due = _add_one_month(base)
    tenant.last_payment_at = now
    tenant.billing_suspended = False
    await db.flush()
    return TenantOut.from_model(tenant)


@router.post("/tenants/{tenant_id}/suspend-billing", response_model=TenantOut)
async def suspend_billing(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> TenantOut:
    """Suspende el servicio de un negocio por falta de pago. El dashboard queda
    bloqueado (402 PAYMENT_OVERDUE) y el agente deja de responder hasta confirmar pago."""
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.billing_suspended = True
    await db.flush()
    return TenantOut.from_model(tenant)


@router.post("/tenants", response_model=TenantOut, status_code=201)
async def create_tenant(
    payload: ProvisionRequest, _: AdminGuard, db: DbSession
) -> TenantOut:
    """Alta manual de un negocio desde el panel del fundador (sin cobro).

    Reutiliza el provisioner: crea tenant + dueño + config de agente/voz +
    automatizaciones por defecto. Los pasos externos (Twilio/Retell/HubSpot)
    se saltan solos si no hay credenciales.
    """
    existing = await db.execute(select(User).where(User.email == str(payload.owner_email)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ese email ya está registrado")
    result = await _provisioner.provision_new_tenant(payload, db)
    tenant = await db.get(Tenant, result["tenant_id"])
    if tenant is None:
        raise HTTPException(status_code=500, detail="No se pudo crear el negocio")
    return TenantOut.from_model(tenant)


@router.post("/tenants/{tenant_id}/provision-voice")
async def provision_voice(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> dict[str, object]:
    """Crea (o re-crea) el agente de voz Retell de un negocio existente sin borrar
    sus datos. Úsalo si el agente de Retell se borró por error o si el negocio pasó
    a un plan con voz después de crearse (cambiar de plan no re-provisiona)."""
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    result = await _provisioner.reprovision_voice(tenant, db)
    await db.flush()
    return {
        "message": f"Voz reconectada para '{tenant.name}'.",
        **result,
    }


async def _reset_user_password(user: User, db: DbSession) -> PasswordResetResult:
    """Genera una clave nueva al azar para un usuario y marca como resueltas sus
    solicitudes pendientes. No se permite sobre cuentas superadmin."""
    if user.role == UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=403,
            detail="Las cuentas de super admin no se restablecen por este flujo.",
        )
    new_password = generate_temp_password()
    user.hashed_password = hash_password(new_password)
    # Cierra cualquier solicitud pendiente de este usuario.
    await db.execute(
        update(PasswordResetRequest)
        .where(
            PasswordResetRequest.user_id == user.id,
            PasswordResetRequest.status == ResetStatus.PENDING,
        )
        .values(status=ResetStatus.RESOLVED, resolved_at=datetime.now(tz=timezone.utc))
    )
    await db.flush()
    return PasswordResetResult(user_email=user.email, new_password=new_password)


@router.get("/password-reset-requests", response_model=list[PasswordResetRequestOut])
async def list_password_reset_requests(
    _: AdminGuard, db: DbSession
) -> list[PasswordResetRequestOut]:
    """Solicitudes de recuperación PENDIENTES de los negocios (las más recientes
    primero), con el nombre del usuario y del negocio para verificar identidad."""
    rows = (
        await db.execute(
            select(PasswordResetRequest, User.full_name, Tenant.name)
            .outerjoin(User, PasswordResetRequest.user_id == User.id)
            .outerjoin(Tenant, PasswordResetRequest.tenant_id == Tenant.id)
            .where(PasswordResetRequest.status == ResetStatus.PENDING)
            .order_by(PasswordResetRequest.created_at.desc())
        )
    ).all()
    return [
        PasswordResetRequestOut(
            id=req.id,
            email=req.email,
            user_id=req.user_id,
            tenant_id=req.tenant_id,
            tenant_name=tenant_name,
            full_name=full_name,
            status=req.status.value,
            created_at=req.created_at,
        )
        for req, full_name, tenant_name in rows
    ]


@router.post(
    "/password-reset-requests/{request_id}/approve",
    response_model=PasswordResetResult,
)
async def approve_password_reset(
    request_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> PasswordResetResult:
    """Aprueba una solicitud: genera una contraseña nueva al azar para el dueño
    y la devuelve UNA vez para que el super admin se la entregue."""
    req = await db.get(PasswordResetRequest, request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if req.user_id is None:
        raise HTTPException(status_code=400, detail="La solicitud no tiene usuario asociado")
    user = await db.get(User, req.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="El usuario ya no existe")
    return await _reset_user_password(user, db)


@router.delete("/password-reset-requests/{request_id}", response_model=MessageResponse)
async def dismiss_password_reset(
    request_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> MessageResponse:
    """Descarta una solicitud (sospechosa o duplicada) sin cambiar la contraseña."""
    req = await db.get(PasswordResetRequest, request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    req.status = ResetStatus.RESOLVED
    req.resolved_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return MessageResponse(message="Solicitud descartada")


@router.post("/tenants/{tenant_id}/reset-owner-password", response_model=PasswordResetResult)
async def reset_owner_password(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> PasswordResetResult:
    """Restablece la contraseña del DUEÑO de un negocio directamente (sin que haya
    una solicitud previa). Útil si el dueño te contacta por otro medio."""
    result = await db.execute(
        select(User)
        .where(User.tenant_id == tenant_id, User.role == UserRole.OWNER)
        .order_by(User.created_at.asc())
    )
    owner = result.scalars().first()
    if owner is None:
        raise HTTPException(status_code=404, detail="El negocio no tiene un dueño registrado")
    return await _reset_user_password(owner, db)


@router.get("/tenants/{tenant_id}/export")
async def export_tenant(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> dict[str, object]:
    """Exporta todos los datos de un tenant (sin secretos) para baja/portabilidad."""
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    async def _rows(model: type) -> list[dict[str, object]]:
        res = await db.execute(select(model).where(model.tenant_id == tenant_id))
        return [_serialize(r) for r in res.scalars().all()]

    return {
        "exported_at": datetime.now(tz=timezone.utc).isoformat(),
        "tenant": _serialize(tenant),
        "users": await _rows(User),
        "agent_configs": await _rows(AgentConfig),
        "voice_configs": await _rows(VoiceConfig),
        "contacts": await _rows(Contact),
        "conversations": await _rows(Conversation),
        "messages": await _rows(Message),
        "calls": await _rows(Call),
        "automations": await _rows(Automation),
        "instagram_posts": await _rows(InstagramPost),
    }


@router.get("/tenants/{tenant_id}/webhooks")
async def tenant_webhook_logs(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession, limit: int = 50
) -> list[dict[str, object]]:
    """Últimos eventos de webhook del tenant (para depurar WhatsApp/voz/etc.)."""
    res = await db.execute(
        select(WebhookLog)
        .where(WebhookLog.tenant_id == tenant_id)
        .order_by(WebhookLog.created_at.desc())
        .limit(min(limit, 200))
    )
    return [_serialize(r) for r in res.scalars().all()]


@router.delete("/tenants/{tenant_id}", response_model=MessageResponse)
async def delete_tenant(
    tenant_id: uuid.UUID, _: AdminGuard, db: DbSession
) -> MessageResponse:
    """Elimina un tenant y TODOS sus datos (cascada en la BD). Irreversible."""
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    name = tenant.name
    await db.execute(delete(Tenant).where(Tenant.id == tenant_id))
    await db.flush()
    return MessageResponse(message=f"Negocio '{name}' eliminado con todos sus datos")
