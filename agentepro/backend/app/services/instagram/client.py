from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"


class InstagramGraphClient:
    """Cliente para Instagram Graph API (DMs y publicación de posts)."""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    async def send_dm(self, instagram_account_id: str, recipient_id: str, message: str) -> dict[str, Any] | None:
        url = f"{GRAPH_BASE}/{instagram_account_id}/messages"
        payload = {"recipient": {"id": recipient_id}, "message": {"text": message}}
        try:
            async with httpx.AsyncClient(timeout=20.0) as http:
                resp = await http.post(
                    url, params={"access_token": self.access_token}, json=payload
                )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("instagram_dm_failed", error=str(exc))
            return None

    async def publish_post(self, instagram_account_id: str, image_url: str, caption: str) -> dict[str, Any] | None:
        """Publica un post en 2 pasos: crea container y luego lo publica."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as http:
                container = await http.post(
                    f"{GRAPH_BASE}/{instagram_account_id}/media",
                    params={"access_token": self.access_token},
                    json={"image_url": image_url, "caption": caption},
                )
                container.raise_for_status()
                creation_id = container.json().get("id")
                if not creation_id:
                    return None
                publish = await http.post(
                    f"{GRAPH_BASE}/{instagram_account_id}/media_publish",
                    params={"access_token": self.access_token},
                    json={"creation_id": creation_id},
                )
                publish.raise_for_status()
                media_id = publish.json().get("id")
                permalink = await self._get_permalink(http, media_id)
                return {"id": media_id, "permalink": permalink}
        except Exception as exc:
            logger.error("instagram_publish_failed", error=str(exc))
            return None

    async def _get_permalink(self, http: httpx.AsyncClient, media_id: str | None) -> str | None:
        if not media_id:
            return None
        try:
            resp = await http.get(
                f"{GRAPH_BASE}/{media_id}",
                params={"fields": "permalink", "access_token": self.access_token},
            )
            return resp.json().get("permalink")
        except Exception:
            return None

    async def get_post_insights(self, media_id: str) -> dict[str, Any] | None:
        try:
            async with httpx.AsyncClient(timeout=20.0) as http:
                resp = await http.get(
                    f"{GRAPH_BASE}/{media_id}",
                    params={
                        "fields": "like_count,comments_count",
                        "access_token": self.access_token,
                    },
                )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("instagram_insights_failed", error=str(exc))
            return None

    @staticmethod
    def get_oauth_url(tenant_slug: str) -> str:
        params = {
            "client_id": settings.META_INSTAGRAM_APP_ID,
            "redirect_uri": f"{settings.FRONTEND_URL}/instagram/callback",
            "scope": "instagram_basic,instagram_content_publish,instagram_manage_messages,pages_show_list",
            "response_type": "code",
            "state": tenant_slug,
        }
        return f"https://www.facebook.com/{GRAPH_VERSION}/dialog/oauth?{urlencode(params)}"
