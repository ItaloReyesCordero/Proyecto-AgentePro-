from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RetellCallEvent(BaseModel):
    """Evento de Retell AI (call_started, call_ended, call_analyzed)."""

    event: str
    call_id: str
    agent_id: str | None = None
    from_number: str | None = None
    to_number: str | None = None
    direction: str | None = None
    transcript: str | None = None
    recording_url: str | None = None
    duration_ms: int | None = None
    disconnection_reason: str | None = None
    metadata: dict[str, Any] = {}
