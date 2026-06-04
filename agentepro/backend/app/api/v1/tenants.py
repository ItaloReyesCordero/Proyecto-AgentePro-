from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.dependencies import CurrentTenant
from app.schemas.tenant import PaymentInfoOut, TenantOut

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/payment-info", response_model=PaymentInfoOut)
async def get_payment_info() -> PaymentInfoOut:
    """Datos de pago del dueño de la plataforma (Yape/transferencia). Público a
    propósito: lo muestra la pantalla de pago, que NO puede llamar endpoints del
    negocio (un trial vencido o suspendido devuelve 402 y entraría en bucle)."""
    return PaymentInfoOut(
        yape_number=settings.PAYMENT_YAPE_NUMBER,
        account_holder=settings.PAYMENT_ACCOUNT_HOLDER,
        bank_account=settings.PAYMENT_BANK_ACCOUNT,
        contact_whatsapp=settings.PAYMENT_CONTACT_WHATSAPP,
        note=settings.PAYMENT_NOTE,
        configured=bool(settings.PAYMENT_YAPE_NUMBER or settings.PAYMENT_BANK_ACCOUNT),
    )


@router.get("/me", response_model=TenantOut)
async def get_my_tenant(tenant: CurrentTenant) -> TenantOut:
    return TenantOut.from_model(tenant)
