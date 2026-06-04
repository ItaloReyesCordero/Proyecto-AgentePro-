from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.plans import FEATURE_VOICE
from app.dependencies import CurrentTenant, DbSession, require_feature
from app.models.voice_config import VoiceConfig
from app.schemas.voice_config import VoiceConfigOut, VoiceConfigUpdate

router = APIRouter(
    prefix="/voice",
    tags=["voice"],
    dependencies=[Depends(require_feature(FEATURE_VOICE))],
)


async def _get_voice(db: DbSession, tenant_id) -> VoiceConfig:
    result = await db.execute(select(VoiceConfig).where(VoiceConfig.tenant_id == tenant_id))
    config = result.scalar_one_or_none()
    if config is None:
        config = VoiceConfig(tenant_id=tenant_id)
        db.add(config)
        await db.flush()
    return config


@router.get("/config", response_model=VoiceConfigOut)
async def get_voice_config(tenant: CurrentTenant, db: DbSession) -> VoiceConfig:
    return await _get_voice(db, tenant.id)


@router.put("/config", response_model=VoiceConfigOut)
async def update_voice_config(
    payload: VoiceConfigUpdate, tenant: CurrentTenant, db: DbSession
) -> VoiceConfig:
    config = await _get_voice(db, tenant.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    await db.flush()
    return config
