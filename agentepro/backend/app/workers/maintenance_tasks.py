from __future__ import annotations

import asyncio

from app.workers.celery_app import celery_app


async def _reset_usage() -> int:
    from sqlalchemy import update

    from app.database import AsyncSessionLocal
    from app.models.tenant import Tenant

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            update(Tenant).values(messages_used_this_month=0, calls_used_this_month=0)
        )
        await db.commit()
        return int(result.rowcount or 0)


@celery_app.task(name="app.workers.maintenance_tasks.reset_monthly_usage")
def reset_monthly_usage() -> int:
    """Reinicia los contadores de uso mensual de todos los tenants (día 1 del mes)."""
    return asyncio.run(_reset_usage())
