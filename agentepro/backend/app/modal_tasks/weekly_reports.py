from __future__ import annotations

import modal

from app.modal_tasks.app import app, image, secrets


@app.function(image=image, schedule=modal.Cron("0 13 * * 1"), secrets=secrets)
async def send_weekly_reports() -> dict[str, int]:
    """Envía un reporte semanal por WhatsApp al propietario de cada tenant activo."""
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.tenant import Tenant
    from app.services import metrics_service
    from app.services.whatsapp.sender import send_whatsapp_message

    sent = 0
    async with AsyncSessionLocal() as db:
        tenants = (
            await db.execute(select(Tenant).where(Tenant.is_active.is_(True)))
        ).scalars().all()

        for tenant in tenants:
            summary = await metrics_service.get_summary(db, tenant.id, "7d")
            cfg = tenant.agent_config
            report = (
                f"📊 *Reporte semanal de {tenant.name}*\n\n"
                f"💬 WhatsApp: {summary.total_messages} mensajes | {summary.new_leads} leads nuevos\n"
                f"📞 Llamadas: {summary.total_calls}\n"
                f"🔥 Leads calientes: {summary.hot_leads_count}\n\n"
                f"Ingresa al dashboard para ver el detalle. 💚"
            )
            phone = cfg.escalation_phone if cfg else None
            if phone and await send_whatsapp_message(tenant, phone, report):
                sent += 1
        await db.commit()

    return {"reports_sent": sent}
