from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

RETELL_BASE_URL = "https://api.retellai.com"


class RetellClient:
    """Cliente REST para Retell AI (agentes de voz con Claude como LLM)."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.RETELL_API_KEY

    @property
    def _enabled(self) -> bool:
        return bool(self.api_key)

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        if not self._enabled:
            logger.info("retell_disabled", path=path)
            return None
        try:
            async with httpx.AsyncClient(timeout=30.0) as http:
                resp = await http.request(
                    method, f"{RETELL_BASE_URL}{path}", headers=self._headers, json=payload
                )
            if resp.status_code >= 400:
                logger.error("retell_error", path=path, status=resp.status_code, body=resp.text[:300])
                return None
            return resp.json()
        except Exception as exc:
            logger.error("retell_request_failed", path=path, error=str(exc))
            return None

    async def create_retell_llm(self, system_prompt: str) -> dict[str, Any] | None:
        """Crea el LLM de Retell. Usa `RETELL_LLM_MODEL` porque Retell exige sus
        propios nombres de modelo (distintos a los de la API de Anthropic)."""
        return await self._request(
            "POST",
            "/create-retell-llm",
            {"model": settings.RETELL_LLM_MODEL, "general_prompt": system_prompt},
        )

    async def create_agent(
        self,
        agent_name: str,
        llm_id: str,
        voice_id: str,
        language: str = "es-419",
        # Retell solo acepta: coffee-shop, convention-hall, summer-outdoor,
        # mountain-outdoor, static-noise, call-center (o None = sin sonido).
        ambient_sound: str | None = None,
        webhook_url: str | None = None,
    ) -> dict[str, Any] | None:
        payload: dict[str, Any] = {
            "agent_name": agent_name,
            "response_engine": {"type": "retell-llm", "llm_id": llm_id},
            "voice_id": voice_id,
            "language": language,
            "enable_backchannel": True,
            "interruption_sensitivity": 0.8,
            "end_call_after_silence_ms": 15000,
        }
        if ambient_sound:
            payload["ambient_sound"] = ambient_sound
        # Sin webhook, Retell NO avisa a nuestro backend cuando termina la llamada
        # → no se guardaría el registro/transcripción/resumen.
        if webhook_url:
            payload["webhook_url"] = webhook_url
        return await self._request("POST", "/create-agent", payload)

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        return await self._request("PATCH", f"/update-agent/{agent_id}", updates)

    async def update_llm(self, llm_id: str, system_prompt: str) -> dict[str, Any] | None:
        return await self._request(
            "PATCH", f"/update-retell-llm/{llm_id}", {"general_prompt": system_prompt}
        )

    async def create_phone_call(
        self, from_number: str, to_number: str, agent_id: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        return await self._request(
            "POST",
            "/v2/create-phone-call",
            {
                "from_number": from_number,
                "to_number": to_number,
                "override_agent_id": agent_id,
                "metadata": metadata or {},
            },
        )

    async def get_call(self, call_id: str) -> dict[str, Any] | None:
        return await self._request("GET", f"/v2/get-call/{call_id}")

    async def delete_agent(self, agent_id: str) -> None:
        await self._request("DELETE", f"/delete-agent/{agent_id}")
