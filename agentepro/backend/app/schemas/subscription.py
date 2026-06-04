from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan: str
    status: str
    amount_cents: int
    currency: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    created_at: datetime


class CreateSubscriptionRequest(BaseModel):
    plan: str
    culqi_token: str
    email: str
