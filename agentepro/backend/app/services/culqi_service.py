from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

CULQI_BASE = "https://api.culqi.com/v2"

# Monto por plan en céntimos de sol (PEN). (Culqi está dormido: se cobra por Yape.)
PLAN_AMOUNTS = {
    "inicial": 14900,
    "basic": 24900,
    "professional": 44900,
    "enterprise": 79900,
}


class CulqiService:
    """Procesa cobros con Culqi (tarjetas y Yape en Perú)."""

    def __init__(self) -> None:
        self.secret_key = settings.CULQI_SECRET_KEY

    @property
    def _enabled(self) -> bool:
        return bool(self.secret_key)

    async def charge(self, token: str, plan: str, email: str) -> dict[str, Any]:
        """Cobra el token de Culqi según el plan. Lanza si falla."""
        amount = PLAN_AMOUNTS.get(plan, PLAN_AMOUNTS["basic"])
        if not self._enabled:
            logger.info("culqi_disabled_simulated_charge", plan=plan, amount=amount)
            return {"id": "chr_simulated", "outcome": {"type": "venta_exitosa"}, "amount": amount}

        payload = {
            "amount": amount,
            "currency_code": "PEN",
            "email": email,
            "source_id": token,
            "description": f"AgentePro plan {plan}",
        }
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.post(
                f"{CULQI_BASE}/charges",
                headers={"Authorization": f"Bearer {self.secret_key}"},
                json=payload,
            )
        if resp.status_code >= 400:
            logger.error("culqi_charge_failed", status=resp.status_code, body=resp.text[:300])
            raise RuntimeError(f"Culqi charge failed: {resp.text[:200]}")
        return resp.json()

    @staticmethod
    def handle_webhook_event(event: dict[str, Any]) -> str:
        """Clasifica un evento de webhook de Culqi. Devuelve la acción a tomar."""
        event_type = event.get("type", "")
        if event_type.startswith("charge.creation") and "success" in event_type:
            return "renew_subscription"
        if "fail" in event_type:
            return "notify_payment_failed"
        if event_type.startswith("subscription.cancel"):
            return "deactivate_tenant"
        return "ignore"
