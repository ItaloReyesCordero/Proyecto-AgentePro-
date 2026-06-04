from __future__ import annotations

from typing import Any

from app.config import settings
from app.core.socket import emit_to_tenant
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def send_email(to: str, subject: str, html: str) -> bool:
    """Envía un email transaccional con Resend. No-op si no hay API key."""
    if not settings.RESEND_API_KEY:
        logger.info("email_skipped_no_key", to=to, subject=subject)
        return False
    try:
        import resend  # import perezoso: dependencia opcional en runtime

        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(
            {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
        return True
    except Exception as exc:
        logger.error("email_send_failed", to=to, error=str(exc))
        return False


async def notify_escalation(
    tenant_id: str,
    *,
    conversation_id: str,
    contact_name: str,
    reason: str,
    escalation_email: str | None = None,
) -> None:
    """Notifica un escalado al dashboard (socket) y por email al negocio."""
    await emit_to_tenant(
        tenant_id,
        "escalation_needed",
        {
            "conversation_id": conversation_id,
            "contact_name": contact_name,
            "reason": reason,
        },
    )
    if escalation_email:
        await send_email(
            to=escalation_email,
            subject=f"🚨 Escalado requerido: {contact_name}",
            html=(
                f"<h2>Un cliente necesita atención humana</h2>"
                f"<p><b>Contacto:</b> {contact_name}</p>"
                f"<p><b>Motivo:</b> {reason}</p>"
                f"<p>Ingresa al dashboard para responder.</p>"
            ),
        )


async def emit_event(tenant_id: str, event: str, data: dict[str, Any]) -> None:
    await emit_to_tenant(tenant_id, event, data)


async def send_welcome_email(
    to: str,
    *,
    business_name: str,
    dashboard_url: str,
    webhook_url: str,
    phone_number: str | None,
    temp_password: str | None = None,
) -> bool:
    html = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <h1 style="color:#10B981;">¡Bienvenido a AgentePro 2.0! 🚀</h1>
      <p>Hola, tu plataforma para <b>{business_name}</b> ya está activa.</p>
      <h3>Tus accesos</h3>
      <ul>
        <li><b>Dashboard:</b> <a href="{dashboard_url}">{dashboard_url}</a></li>
        <li><b>URL de webhook de WhatsApp (Meta):</b><br><code>{webhook_url}</code></li>
        <li><b>Número telefónico asignado:</b> {phone_number or "Pendiente"}</li>
        {f"<li><b>Contraseña temporal:</b> {temp_password}</li>" if temp_password else ""}
      </ul>
      <h3>Próximos pasos</h3>
      <ol>
        <li>Conecta tu WhatsApp Business en developers.facebook.com.</li>
        <li>Pega la URL del webhook y el token de verificación.</li>
        <li>Configura tu agente IA en el dashboard.</li>
      </ol>
      <p>¡Tu negocio ahora atiende 24/7! 💚</p>
    </div>
    """
    return await send_email(to, f"Bienvenido a AgentePro — {business_name}", html)
