from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.call import Call


class CallSummary(Base):
    __tablename__ = "call_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("calls.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # AI-Generated Summary
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    action_items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    topics_discussed: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Sentiment & Classification
    overall_sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    customer_satisfaction_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    call_outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    follow_up_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lead / Sales Info
    intent_detected: Mapped[str | None] = mapped_column(String(100), nullable=True)
    products_mentioned: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    objections_raised: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)

    # HubSpot Sync
    hubspot_note_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hubspot_task_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # AI Usage
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    call: Mapped[Call] = relationship("Call", back_populates="summary")

    def __repr__(self) -> str:
        return f"<CallSummary(id={self.id}, call_id={self.call_id}, outcome={self.call_outcome})>"
