from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

HUBSPOT_BASE = "https://api.hubapi.com"

# Mapeo de etapas internas -> lifecycle stage de HubSpot.
_LIFECYCLE_MAP = {
    "cold": "lead",
    "warm": "marketingqualifiedlead",
    "hot": "salesqualifiedlead",
    "customer": "customer",
    "lost": "other",
}


class HubSpotClient:
    """Cliente REST mínimo para HubSpot (CRM v3)."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token or settings.HUBSPOT_ACCESS_TOKEN

    @property
    def _enabled(self) -> bool:
        return bool(self.access_token)

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self._enabled:
            logger.info("hubspot_disabled", path=path)
            return None
        try:
            async with httpx.AsyncClient(timeout=20.0) as http:
                resp = await http.post(f"{HUBSPOT_BASE}{path}", headers=self._headers, json=payload)
            if resp.status_code >= 400:
                logger.error("hubspot_error", path=path, status=resp.status_code, body=resp.text[:300])
                return None
            return resp.json()
        except Exception as exc:
            logger.error("hubspot_request_failed", path=path, error=str(exc))
            return None

    async def create_or_update_contact(
        self,
        phone: str,
        name: str | None = None,
        email: str | None = None,
        lead_score: int | None = None,
        lead_stage: str | None = None,
        source: str | None = None,
        tenant_id: str | None = None,
    ) -> str | None:
        """Crea o actualiza un contacto. Devuelve el hubspot_contact_id."""
        first, _, last = (name or "").partition(" ")
        props: dict[str, Any] = {"phone": phone}
        if first:
            props["firstname"] = first
        if last:
            props["lastname"] = last
        if email:
            props["email"] = email
        if lead_stage:
            props["lifecyclestage"] = _LIFECYCLE_MAP.get(lead_stage, "lead")
        props["last_interaction_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Intenta búsqueda por teléfono, luego crea/actualiza.
        search = await self._post(
            "/crm/v3/objects/contacts/search",
            {
                "filterGroups": [
                    {"filters": [{"propertyName": "phone", "operator": "EQ", "value": phone}]}
                ],
                "limit": 1,
            },
        )
        existing_id = None
        if search and search.get("results"):
            existing_id = search["results"][0].get("id")

        if existing_id:
            result = await self._post(
                f"/crm/v3/objects/contacts/{existing_id}", {"properties": props}
            )
            return existing_id if result is None else result.get("id", existing_id)

        created = await self._post("/crm/v3/objects/contacts", {"properties": props})
        return created.get("id") if created else None

    async def create_deal(
        self,
        contact_id: str,
        deal_name: str,
        stage: str = "appointmentscheduled",
        amount: float | None = None,
    ) -> str | None:
        props: dict[str, Any] = {"dealname": deal_name, "dealstage": stage, "pipeline": "default"}
        if amount is not None:
            props["amount"] = amount
        created = await self._post("/crm/v3/objects/deals", {"properties": props})
        deal_id = created.get("id") if created else None
        if deal_id and contact_id:
            await self._post(
                f"/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/3",
                {},
            )
        return deal_id

    async def add_activity_note(self, contact_id: str, note: str) -> str | None:
        created = await self._post(
            "/crm/v3/objects/notes",
            {
                "properties": {
                    "hs_note_body": note,
                    "hs_timestamp": datetime.now(timezone.utc).isoformat(),
                }
            },
        )
        note_id = created.get("id") if created else None
        if note_id:
            await self._post(
                f"/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/202",
                {},
            )
        return note_id

    async def create_task(self, contact_id: str, title: str, notes: str | None = None) -> str | None:
        created = await self._post(
            "/crm/v3/objects/tasks",
            {
                "properties": {
                    "hs_task_subject": title,
                    "hs_task_body": notes or "",
                    "hs_task_status": "NOT_STARTED",
                    "hs_timestamp": datetime.now(timezone.utc).isoformat(),
                }
            },
        )
        task_id = created.get("id") if created else None
        if task_id:
            await self._post(
                f"/crm/v3/objects/tasks/{task_id}/associations/contacts/{contact_id}/204",
                {},
            )
        return task_id

    async def setup_tenant_company(self, company_name: str) -> str | None:
        created = await self._post(
            "/crm/v3/objects/companies", {"properties": {"name": company_name}}
        )
        return created.get("id") if created else None
