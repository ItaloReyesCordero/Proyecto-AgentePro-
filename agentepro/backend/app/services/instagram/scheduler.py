from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instagram_post import InstagramPost, InstagramPostStatus
from app.models.tenant import Tenant
from app.services.instagram.client import InstagramGraphClient
from app.utils.encryption import decrypt_if_value
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def publish_due_posts(db: AsyncSession) -> int:
    """Publica los posts cuyo scheduled_for ya venció. Devuelve cuántos se publicaron."""
    now = datetime.now(tz=timezone.utc)
    result = await db.execute(
        select(InstagramPost).where(
            InstagramPost.status == InstagramPostStatus.SCHEDULED,
            InstagramPost.scheduled_for <= now,
        )
    )
    posts = list(result.scalars().all())
    published = 0
    for post in posts:
        tenant = await db.get(Tenant, post.tenant_id)
        if tenant is None or not tenant.instagram_account_id or not tenant.instagram_access_token:
            post.status = InstagramPostStatus.FAILED
            post.error_message = "Instagram no conectado."
            continue
        token = decrypt_if_value(tenant.instagram_access_token)
        image_url = post.ai_generated_image_url or (post.media_urls[0] if post.media_urls else None)
        if not token or not image_url:
            post.status = InstagramPostStatus.FAILED
            post.error_message = "Faltan credenciales o imagen."
            continue
        client = InstagramGraphClient(token)
        result_pub = await client.publish_post(
            tenant.instagram_account_id, image_url, post.caption or ""
        )
        if result_pub and result_pub.get("id"):
            post.status = InstagramPostStatus.PUBLISHED
            post.instagram_media_id = result_pub["id"]
            post.published_at = now
            published += 1
        else:
            post.status = InstagramPostStatus.FAILED
            post.error_message = "Falló la publicación en Instagram."
    await db.flush()
    return published
