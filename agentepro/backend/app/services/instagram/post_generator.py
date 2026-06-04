from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_config import AgentConfig
from app.models.instagram_post import InstagramMediaType, InstagramPost, InstagramPostStatus
from app.models.tenant import Tenant
from app.services.ai.instagram_content_generator import InstagramContentGenerator
from app.utils.helpers import enum_value
from app.utils.logger import get_logger

logger = get_logger(__name__)

_generator = InstagramContentGenerator()


async def generate_and_store_post(
    db: AsyncSession,
    tenant: Tenant,
    agent_config: AgentConfig | None,
    topic: str,
    generate_image: bool = True,
) -> InstagramPost:
    """Genera un post con IA + imagen y lo guarda como pendiente de aprobación."""
    services = agent_config.services if agent_config else []
    generated = await _generator.generate_post(
        topic=topic,
        business_name=tenant.name,
        business_type=enum_value(tenant.business_type),
        services=services,
        tone="profesional",
        generate_image=generate_image,
    )

    post = InstagramPost(
        tenant_id=tenant.id,
        media_type=InstagramMediaType.IMAGE,
        caption=generated.caption,
        ai_generated_caption=generated.caption,
        ai_generated_image_url=generated.image_url,
        media_urls=[generated.image_url] if generated.image_url else [],
        prompt_used=generated.image_prompt,
        hashtags=generated.hashtags,
        status=InstagramPostStatus.DRAFT,
        post_metadata={"pending_approval": True},
    )
    db.add(post)
    await db.flush()
    logger.info("instagram_post_generated", tenant_id=str(tenant.id), post_id=str(post.id))
    return post
