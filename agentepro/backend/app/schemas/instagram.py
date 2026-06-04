from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.instagram_post import InstagramPost
from app.utils.helpers import enum_value

# Estados internos -> estados del frontend.
_STATUS_MAP = {
    "draft": "draft",
    "scheduled": "scheduled",
    "publishing": "scheduled",
    "published": "published",
    "failed": "rejected",
}


class InstagramPostOut(BaseModel):
    id: uuid.UUID
    caption: str
    image_url: str | None
    status: str
    scheduled_for: datetime | None
    published_at: datetime | None
    created_at: datetime
    likes_count: int
    comments_count: int
    ai_generated: bool
    hashtags: list[str]

    @classmethod
    def from_model(cls, p: InstagramPost) -> "InstagramPostOut":
        image_url = p.ai_generated_image_url or (p.media_urls[0] if p.media_urls else None)
        raw_status = enum_value(p.status)
        # Estado lógico de aprobación guardado en post_metadata.
        meta = p.post_metadata or {}
        if meta.get("pending_approval") and raw_status == "draft":
            status = "pending_approval"
        elif meta.get("rejected"):
            status = "rejected"
        else:
            status = _STATUS_MAP.get(raw_status, "draft")
        return cls(
            id=p.id,
            caption=p.caption or p.ai_generated_caption or "",
            image_url=image_url,
            status=status,
            scheduled_for=p.scheduled_for,
            published_at=p.published_at,
            created_at=p.created_at,
            likes_count=p.likes_count,
            comments_count=p.comments_count,
            ai_generated=bool(p.ai_generated_caption),
            hashtags=p.hashtags or [],
        )


class GeneratePostsRequest(BaseModel):
    week_start: str | None = None
    count: int = 3
    topics: list[str] | None = None


class ApprovePostRequest(BaseModel):
    caption: str | None = None
    scheduled_for: datetime | None = None


class RejectPostRequest(BaseModel):
    reason: str | None = None
