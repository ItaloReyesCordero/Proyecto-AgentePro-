from __future__ import annotations

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def seed_superadmin() -> None:
    """Crea la cuenta de super admin del fundador si no existe.

    Idempotente: si ya hay un usuario con el email configurado, no hace nada.
    El superadmin no pertenece a ningún tenant (tenant_id = NULL) y administra
    toda la plataforma.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == settings.SUPERADMIN_EMAIL)
        )
        if result.scalar_one_or_none() is not None:
            return

        admin = User(
            tenant_id=None,
            email=settings.SUPERADMIN_EMAIL,
            hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
            full_name=settings.SUPERADMIN_NAME,
            role=UserRole.SUPERADMIN,
        )
        db.add(admin)
        await db.commit()
        logger.info("superadmin_seeded", email=settings.SUPERADMIN_EMAIL)
