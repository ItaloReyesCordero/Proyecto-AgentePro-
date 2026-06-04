from __future__ import annotations

import modal

from app.modal_tasks.app import app, image, secrets


@app.function(image=image, schedule=modal.Cron("0 13 * * 1"), secrets=secrets)
async def generate_weekly_instagram_posts() -> dict[str, int]:
    """Genera 3 posts semanales por tenant Pro/Enterprise con Instagram conectado."""
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.instagram_post import InstagramPostStatus
    from app.models.tenant import PlanType, Tenant
    from app.services.instagram.post_generator import generate_and_store_post
    from app.services.notification_service import emit_event

    topics = ["servicio destacado", "promoción de la semana", "consejo útil"]
    generated = 0

    async with AsyncSessionLocal() as db:
        tenants = (
            await db.execute(
                select(Tenant).where(
                    Tenant.is_active.is_(True),
                    Tenant.plan.in_([PlanType.PROFESSIONAL, PlanType.ENTERPRISE]),
                    Tenant.instagram_account_id.isnot(None),
                )
            )
        ).scalars().all()

        # martes, jueves, sábado 12pm
        post_days = [1, 3, 5]
        base = datetime.now(tz=timezone.utc).replace(hour=17, minute=0, second=0, microsecond=0)

        for tenant in tenants:
            for i, topic in enumerate(topics):
                post = await generate_and_store_post(db, tenant, tenant.agent_config, topic)
                post.scheduled_for = base + timedelta(days=post_days[i % 3])
                post.status = InstagramPostStatus.SCHEDULED
                post.post_metadata = {**(post.post_metadata or {}), "pending_approval": True}
                generated += 1
            await emit_event(str(tenant.id), "instagram_post_ready", {"count": len(topics)})
        await db.commit()

    return {"posts_generated": generated}


@app.function(image=image, schedule=modal.Cron("0 * * * *"), secrets=secrets)
async def publish_scheduled_posts() -> dict[str, int]:
    """Cada hora: publica los posts programados cuyo horario ya venció."""
    from app.database import AsyncSessionLocal
    from app.services.instagram.scheduler import publish_due_posts

    async with AsyncSessionLocal() as db:
        published = await publish_due_posts(db)
        await db.commit()
    return {"published": published}
