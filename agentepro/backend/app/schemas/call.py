from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.call import Call
from app.models.call_summary import CallSummary as CallSummaryModel
from app.models.contact import Contact
from app.utils.helpers import enum_value


class CallContactOut(BaseModel):
    id: uuid.UUID
    name: str | None
    phone: str | None


class CallSummaryOut(BaseModel):
    id: uuid.UUID
    key_points: list[str]
    action_items: list[str]
    sentiment: str
    follow_up_required: bool
    follow_up_date: datetime | None
    follow_up_notes: str | None

    @classmethod
    def from_model(cls, s: CallSummaryModel) -> "CallSummaryOut":
        action_items = [
            ai if isinstance(ai, str) else ai.get("text", str(ai))
            for ai in (s.action_items or [])
        ]
        return cls(
            id=s.id,
            key_points=s.key_points or [],
            action_items=action_items,
            sentiment=s.overall_sentiment or "neutral",
            follow_up_required=s.follow_up_required,
            follow_up_date=None,
            follow_up_notes=s.follow_up_notes,
        )


class CallOut(BaseModel):
    id: uuid.UUID
    contact: CallContactOut | None
    direction: str
    from_number: str
    to_number: str
    status: str
    duration_seconds: int
    recording_url: str | None
    transcript: str | None
    ai_summary: str | None
    intent_detected: str | None
    outcome: str | None
    lead_score_before: int = 0
    lead_score_after: int = 0
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime
    summary: CallSummaryOut | None = None

    @classmethod
    def from_model(
        cls,
        call: Call,
        contact: Contact | None = None,
        summary: CallSummaryModel | None = None,
    ) -> "CallOut":
        contact_out = None
        if contact is not None:
            contact_out = CallContactOut(
                id=contact.id, name=contact.full_name, phone=contact.phone_number
            )
        return cls(
            id=call.id,
            contact=contact_out,
            direction=enum_value(call.direction),
            from_number=call.from_number or "",
            to_number=call.to_number or "",
            status=enum_value(call.status),
            duration_seconds=call.duration_seconds or 0,
            recording_url=call.recording_url,
            transcript=call.transcription,
            ai_summary=summary.summary if summary else None,
            intent_detected=call.intent,
            outcome=summary.call_outcome if summary else None,
            started_at=call.started_at,
            ended_at=call.ended_at,
            created_at=call.created_at,
            summary=CallSummaryOut.from_model(summary) if summary else None,
        )


class OutboundCallRequest(BaseModel):
    to_number: str
    contact_id: uuid.UUID | None = None
    reason: str = "follow_up"
