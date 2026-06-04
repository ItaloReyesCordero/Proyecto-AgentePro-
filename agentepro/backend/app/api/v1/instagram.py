from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from app.core.plans import FEATURE_INSTAGRAM
from app.dependencies import CurrentTenant, DbSession, require_feature
from app.models.agent_config import AgentConfig
from app.models.instagram_post import InstagramPost, InstagramPostStatus
from app.models.tenant import Tenant
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.instagram import (
    ApprovePostRequest,
    GeneratePostsRequest,
    InstagramPostOut,
    RejectPostRequest,
)
from app.services.instagram.client import InstagramGraphClient
from app.services.instagram.post_generator import generate_and_store_post
from app.utils.encryption import decrypt_if_value

router = APIRouter(
    prefix="/instagram",
    tags=["instagram"],
    dependencies=[Depends(require_feature(FEATURE_INSTAGRAM))],
)


async def _require(db: DbSession, tenant: Tenant, post_id: uuid.UUID) -> InstagramPost:
    result = await db.execute(
        select(InstagramPost).where(
            InstagramPost.id == post_id, InstagramPost.tenant_id == tenant.id
        )
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/posts", response_model=PaginatedResponse[InstagramPostOut])
async def list_posts(
    tenant: CurrentTenant,
    db: DbSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
) -> PaginatedResponse[InstagramPostOut]:
    total_res = await db.execute(
        select(func.count(InstagramPost.id)).where(InstagramPost.tenant_id == tenant.id)
    )
    total = int(total_res.scalar() or 0)
    result = await db.execute(
        select(InstagramPost)
        .where(InstagramPost.tenant_id == tenant.id)
        .order_by(InstagramPost.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    items = [InstagramPostOut.from_model(p) for p in result.scalars().all()]
    return PaginatedResponse.build(items, total, page, per_page)


@router.post("/posts/generate", response_model=list[InstagramPostOut])
async def generate_posts(
    payload: GeneratePostsRequest, tenant: CurrentTenant, db: DbSession
) -> list[InstagramPostOut]:
    cfg_res = await db.execute(select(AgentConfig).where(AgentConfig.tenant_id == tenant.id))
    agent_config = cfg_res.scalar_one_or_none()
    topics = payload.topics or ["servicio destacado", "promoción", "consejo útil"]
    topics = topics[: payload.count]
    posts: list[InstagramPostOut] = []
    for topic in topics:
        post = await generate_and_store_post(db, tenant, agent_config, topic)
        posts.append(InstagramPostOut.from_model(post))
    return posts


@router.get("/posts/{post_id}", response_model=InstagramPostOut)
async def get_post(post_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> InstagramPostOut:
    return InstagramPostOut.from_model(await _require(db, tenant, post_id))


@router.post("/posts/{post_id}/approve", response_model=InstagramPostOut)
async def approve_post(
    post_id: uuid.UUID, payload: ApprovePostRequest, tenant: CurrentTenant, db: DbSession
) -> InstagramPostOut:
    post = await _require(db, tenant, post_id)
    if payload.caption:
        post.caption = payload.caption
    post.scheduled_for = payload.scheduled_for or datetime.now(tz=timezone.utc)
    post.status = InstagramPostStatus.SCHEDULED
    post.post_metadata = {**(post.post_metadata or {}), "pending_approval": False}
    await db.flush()
    return InstagramPostOut.from_model(post)


@router.post("/posts/{post_id}/reject", response_model=InstagramPostOut)
async def reject_post(
    post_id: uuid.UUID, tenant: CurrentTenant, db: DbSession, payload: RejectPostRequest | None = None
) -> InstagramPostOut:
    post = await _require(db, tenant, post_id)
    post.status = InstagramPostStatus.DRAFT
    post.post_metadata = {
        **(post.post_metadata or {}),
        "pending_approval": False,
        "rejected": True,
        "rejection_reason": payload.reason if payload else None,
    }
    await db.flush()
    return InstagramPostOut.from_model(post)


@router.post("/posts/{post_id}/publish", response_model=InstagramPostOut)
async def publish_post(post_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> InstagramPostOut:
    post = await _require(db, tenant, post_id)
    if not tenant.instagram_account_id or not tenant.instagram_access_token:
        raise HTTPException(status_code=400, detail="Instagram no conectado")
    token = decrypt_if_value(tenant.instagram_access_token)
    image_url = post.ai_generated_image_url or (post.media_urls[0] if post.media_urls else None)
    if not token or not image_url:
        raise HTTPException(status_code=400, detail="Faltan credenciales o imagen")
    result = await InstagramGraphClient(token).publish_post(
        tenant.instagram_account_id, image_url, post.caption or ""
    )
    if not result or not result.get("id"):
        post.status = InstagramPostStatus.FAILED
        await db.flush()
        raise HTTPException(status_code=502, detail="Falló la publicación")
    post.status = InstagramPostStatus.PUBLISHED
    post.instagram_media_id = result["id"]
    post.published_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return InstagramPostOut.from_model(post)


@router.delete("/posts/{post_id}", response_model=MessageResponse)
async def delete_post(post_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> MessageResponse:
    post = await _require(db, tenant, post_id)
    await db.delete(post)
    await db.flush()
    return MessageResponse(message="Post eliminado")


@router.get("/connect-url")
async def connect_url(tenant: CurrentTenant) -> dict[str, str]:
    return {"url": InstagramGraphClient.get_oauth_url(tenant.slug)}
