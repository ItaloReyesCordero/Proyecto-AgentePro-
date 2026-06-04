from __future__ import annotations

from typing import Any

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

GRAPH_API_VERSION = "v21.0"
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class WhatsAppClient:
    """Cliente para la WhatsApp Cloud API (Meta Graph API).

    Cada instancia se construye con las credenciales DESENCRIPTADAS del tenant.
    """

    def __init__(self, phone_number_id: str, access_token: str) -> None:
        self.phone_number_id = phone_number_id
        self.access_token = access_token

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_text(self, to: str, text: str) -> dict[str, Any]:
        """Envía un mensaje de texto. Devuelve la respuesta de Meta."""
        url = f"{GRAPH_BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": True, "body": text[:4096]},
        }
        async with httpx.AsyncClient(timeout=20.0) as http:
            resp = await http.post(url, headers=self._headers, json=payload)
        if resp.status_code >= 400:
            logger.error("whatsapp_send_error", status=resp.status_code, body=resp.text[:300])
            resp.raise_for_status()
        return resp.json()

    async def mark_as_read(self, message_id: str) -> None:
        """Marca un mensaje entrante como leído (doble check azul)."""
        url = f"{GRAPH_BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as http:
                await http.post(url, headers=self._headers, json=payload)
        except Exception as exc:  # pragma: no cover - best effort
            logger.warning("whatsapp_mark_read_failed", error=str(exc))

    async def send_typing_indicator(self, message_id: str) -> None:
        """Indicador de 'escribiendo...' (best-effort; requiere API compatible)."""
        url = f"{GRAPH_BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
            "typing_indicator": {"type": "text"},
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as http:
                await http.post(url, headers=self._headers, json=payload)
        except Exception:  # pragma: no cover - opcional
            pass

    async def get_media_url(self, media_id: str) -> str | None:
        """Resuelve la URL temporal de descarga de un media de WhatsApp."""
        url = f"{GRAPH_BASE_URL}/{media_id}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as http:
                resp = await http.get(url, headers={"Authorization": f"Bearer {self.access_token}"})
            resp.raise_for_status()
            return resp.json().get("url")
        except Exception as exc:
            logger.warning("whatsapp_media_url_failed", error=str(exc))
            return None

    async def download_media(self, media_url: str) -> bytes | None:
        """Descarga los bytes de un media usando la URL temporal de Meta."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as http:
                resp = await http.get(
                    media_url, headers={"Authorization": f"Bearer {self.access_token}"}
                )
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            logger.warning("whatsapp_media_download_failed", error=str(exc))
            return None
