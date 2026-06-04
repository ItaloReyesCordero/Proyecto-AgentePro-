from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class InstagramPostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class InstagramMediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    REEL = "reel"
    STORY = "story"


class InstagramPost(Base):
    __tablename__ = "instagram_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # External IDs
    instagram_media_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    instagram_container_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Content
    media_type: Mapped[InstagramMediaType] = mapped_column(
        SAEnum(InstagramMediaType, name="instagram_media_type_enum"),
        nullable=False,
        default=InstagramMediaType.IMAGE,
    )
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_urls: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    hashtags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # AI Generation
    ai_generated_caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_generated_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    fal_request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status & Scheduling
    status: Mapped[InstagramPostStatus] = mapped_column(
        SAEnum(InstagramPostStatus, name="instagram_post_status_enum"),
        nullable=False,
        default=InstagramPostStatus.DRAFT,
        index=True,
    )
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metrics (refreshed from Instagram API)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reach: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    saves: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metrics_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Additional metadata (attribute renamed from reserved `metadata`)
    post_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="instagram_posts")

    def __repr__(self) -> str:
        return f"<InstagramPost(id={self.id}, status={self.status}, media_type={self.media_type})>"
