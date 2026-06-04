from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.automation import Automation
from app.models.automation_run import AutomationRun
from app.utils.helpers import enum_value

# Mapeo de tipo interno -> trigger del frontend.
_TRIGGER_MAP = {
    "follow_up": "no_response_24h",
    "lead_nurturing": "lead_stage_change",
    "reactivation": "no_response_24h",
    "appointment_reminder": "appointment_reminder",
    "broadcast": "schedule",
    "drip_campaign": "schedule",
    "custom": "schedule",
}


class AutomationExecutionOut(BaseModel):
    id: uuid.UUID
    executed_at: datetime
    status: str
    contact_name: str | None
    notes: str | None

    @classmethod
    def from_model(cls, run: AutomationRun) -> "AutomationExecutionOut":
        status = enum_value(run.status)
        status = {"completed": "success", "failed": "failed", "running": "skipped"}.get(
            status, "skipped"
        )
        return cls(
            id=run.id,
            executed_at=run.completed_at or run.created_at,
            status=status,
            contact_name=None,
            notes=f"{run.messages_sent} mensajes enviados",
        )


class AutomationOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    trigger: str
    is_active: bool
    execution_count: int
    last_executed_at: datetime | None
    created_at: datetime
    recent_executions: list[AutomationExecutionOut]

    @classmethod
    def from_model(
        cls, a: Automation, recent: list[AutomationRun] | None = None
    ) -> "AutomationOut":
        return cls(
            id=a.id,
            name=a.name,
            description=a.description or "",
            trigger=_TRIGGER_MAP.get(enum_value(a.automation_type), "schedule"),
            is_active=enum_value(a.status) == "active",
            execution_count=a.total_runs,
            last_executed_at=a.last_run_at,
            created_at=a.created_at,
            recent_executions=[AutomationExecutionOut.from_model(r) for r in (recent or [])],
        )


class AutomationUpdate(BaseModel):
    is_active: bool | None = None
    name: str | None = None
    description: str | None = None
    trigger_config: dict | None = None
