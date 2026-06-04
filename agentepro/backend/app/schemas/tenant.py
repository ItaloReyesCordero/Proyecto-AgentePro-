from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.plans import call_limit, message_limit, plan_features
from app.models.tenant import Tenant
from app.utils.helpers import enum_value


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    business_type: str
    plan: str
    is_active: bool
    is_provisioned: bool
    twilio_phone_number: str | None
    messages_used_this_month: int
    calls_used_this_month: int
    trial_ends_at: datetime | None
    created_at: datetime
    # Plan: módulos habilitados + topes (para que el frontend muestre/oculte y
    # avise "vas X/Y mensajes"). Derivados del plan, no se persisten.
    features: list[str] = []
    message_limit: int = 0
    call_limit: int = 0
    # Cobro manual
    next_payment_due: datetime | None = None
    last_payment_at: datetime | None = None
    monthly_amount_pen: int | None = None
    billing_suspended: bool = False
    payment_state: str = "active"
    payment_due_at: datetime | None = None

    @classmethod
    def from_model(cls, t: Tenant) -> "TenantOut":
        return cls(
            id=t.id,
            name=t.name,
            slug=t.slug,
            business_type=enum_value(t.business_type),
            plan=enum_value(t.plan),
            is_active=t.is_active,
            is_provisioned=t.is_provisioned,
            twilio_phone_number=t.twilio_phone_number,
            messages_used_this_month=t.messages_used_this_month,
            calls_used_this_month=t.calls_used_this_month,
            trial_ends_at=t.trial_ends_at,
            created_at=t.created_at,
            features=sorted(plan_features(t.plan)),
            message_limit=message_limit(t.plan),
            call_limit=call_limit(t.plan),
            next_payment_due=t.next_payment_due,
            last_payment_at=t.last_payment_at,
            monthly_amount_pen=t.monthly_amount_pen,
            billing_suspended=t.billing_suspended,
            payment_state=t.payment_state,
            payment_due_at=t.payment_due_at,
        )


class BillingPendingOut(BaseModel):
    """Fila de la lista 'Cobros por revisar' del panel del fundador."""
    id: uuid.UUID
    name: str
    plan: str
    payment_state: str  # due_soon | overdue | suspended
    due_at: datetime | None
    days_overdue: int  # >0 vencido; <0 faltan días; 0 vence hoy
    amount_pen: int
    is_active: bool


class ConfirmPaymentRequest(BaseModel):
    """Confirma un pago recibido (Yape/transferencia). Opcionalmente fija plan/monto."""
    plan: str | None = None
    amount_pen: int | None = None


class PaymentInfoOut(BaseModel):
    """Datos de pago públicos que ve el negocio en la pantalla de pago."""
    yape_number: str
    account_holder: str
    bank_account: str
    contact_whatsapp: str
    note: str
    configured: bool


class TenantCreate(BaseModel):
    name: str
    business_type: str = "other"
    owner_name: str
    owner_email: EmailStr
    owner_phone: str
    plan: str = "basic"


class TenantUpdate(BaseModel):
    name: str | None = None
    plan: str | None = None
    is_active: bool | None = None


class ProvisionRequest(BaseModel):
    business_name: str
    business_type: str = "other"
    owner_name: str
    owner_email: EmailStr
    owner_phone: str
    plan: str = "basic"
    culqi_token: str | None = None
    password: str | None = None  # si se provee, el dueño la usa para iniciar sesión


class ProvisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: uuid.UUID
    dashboard_url: str
    webhook_url: str
    phone_number: str | None
    access_token: str
