from __future__ import annotations

from pydantic import BaseModel


class MessageVolumePoint(BaseModel):
    date: str
    count: int


class LeadsFunnelPoint(BaseModel):
    stage: str
    count: int


class MetricsSummary(BaseModel):
    total_messages: int
    messages_today: int
    messages_change_pct: float
    new_leads: int
    leads_change_pct: float
    appointments_booked: int
    total_calls: int
    avg_response_time_minutes: float
    hot_leads_count: int
    message_volume_chart: list[MessageVolumePoint]
    leads_funnel: list[LeadsFunnelPoint]


class CostBreakdown(BaseModel):
    claude_usd: float
    twilio_usd: float
    retell_usd: float
    fal_usd: float
    total_usd: float
    tokens_used: int
    calls_count: int
