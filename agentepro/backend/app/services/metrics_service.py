from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.call import Call
from app.models.call_summary import CallSummary
from app.models.contact import Contact
from app.models.message import Message, MessageDirection
from app.schemas.metrics import (
    CostBreakdown,
    LeadsFunnelPoint,
    MessageVolumePoint,
    MetricsSummary,
)

_PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90}


def _period_days(period: str) -> int:
    return _PERIOD_DAYS.get(period, 7)


def _pct_change(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)


async def _count_messages(db: AsyncSession, tenant_id: uuid.UUID, since: datetime, until: datetime) -> int:
    result = await db.execute(
        select(func.count(Message.id)).where(
            Message.tenant_id == tenant_id,
            Message.created_at >= since,
            Message.created_at < until,
        )
    )
    return int(result.scalar() or 0)


async def get_message_volume(
    db: AsyncSession, tenant_id: uuid.UUID, period: str = "7d"
) -> list[MessageVolumePoint]:
    days = _period_days(period)
    now = datetime.now(tz=timezone.utc)
    points: list[MessageVolumePoint] = []
    for i in range(days - 1, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = await _count_messages(db, tenant_id, day_start, day_end)
        points.append(MessageVolumePoint(date=day_start.strftime("%Y-%m-%d"), count=count))
    return points


async def get_leads_funnel(db: AsyncSession, tenant_id: uuid.UUID) -> list[LeadsFunnelPoint]:
    result = await db.execute(
        select(Contact.qualification_score, Contact.status).where(Contact.tenant_id == tenant_id)
    )
    buckets = {"cold": 0, "warm": 0, "hot": 0, "customer": 0}
    for score, status in result.all():
        status_val = status.value if hasattr(status, "value") else status
        if status_val == "customer":
            buckets["customer"] += 1
        elif (score or 0) >= 67:
            buckets["hot"] += 1
        elif (score or 0) >= 34:
            buckets["warm"] += 1
        else:
            buckets["cold"] += 1
    return [LeadsFunnelPoint(stage=k, count=v) for k, v in buckets.items()]


async def get_summary(db: AsyncSession, tenant_id: uuid.UUID, period: str = "7d") -> MetricsSummary:
    days = _period_days(period)
    now = datetime.now(tz=timezone.utc)
    period_start = now - timedelta(days=days)
    prev_start = now - timedelta(days=days * 2)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_messages = await _count_messages(db, tenant_id, period_start, now)
    prev_messages = await _count_messages(db, tenant_id, prev_start, period_start)
    messages_today = await _count_messages(db, tenant_id, today_start, now)

    new_leads_res = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.tenant_id == tenant_id, Contact.created_at >= period_start
        )
    )
    new_leads = int(new_leads_res.scalar() or 0)
    prev_leads_res = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.tenant_id == tenant_id,
            Contact.created_at >= prev_start,
            Contact.created_at < period_start,
        )
    )
    prev_leads = int(prev_leads_res.scalar() or 0)

    hot_res = await db.execute(
        select(func.count(Contact.id)).where(
            Contact.tenant_id == tenant_id, Contact.qualification_score >= 67
        )
    )
    hot_leads = int(hot_res.scalar() or 0)

    calls_res = await db.execute(
        select(func.count(Call.id)).where(
            Call.tenant_id == tenant_id, Call.created_at >= period_start
        )
    )
    total_calls = int(calls_res.scalar() or 0)

    # Citas agendadas: resúmenes de llamada con outcome 'appointment_booked'
    appts_res = await db.execute(
        select(func.count(CallSummary.id))
        .join(Call, Call.id == CallSummary.call_id)
        .where(
            Call.tenant_id == tenant_id,
            CallSummary.call_outcome == "appointment_booked",
            CallSummary.created_at >= period_start,
        )
    )
    appointments_booked = int(appts_res.scalar() or 0)

    avg_response = await _avg_response_time_minutes(db, tenant_id, period_start)

    funnel = await get_leads_funnel(db, tenant_id)
    volume = await get_message_volume(db, tenant_id, period)

    return MetricsSummary(
        total_messages=total_messages,
        messages_today=messages_today,
        messages_change_pct=_pct_change(total_messages, prev_messages),
        new_leads=new_leads,
        leads_change_pct=_pct_change(new_leads, prev_leads),
        appointments_booked=appointments_booked,
        total_calls=total_calls,
        avg_response_time_minutes=avg_response,
        hot_leads_count=hot_leads,
        message_volume_chart=volume,
        leads_funnel=funnel,
    )


async def _avg_response_time_minutes(
    db: AsyncSession, tenant_id: uuid.UUID, since: datetime
) -> float:
    """Tiempo promedio (min) entre un mensaje entrante y la siguiente respuesta saliente."""
    result = await db.execute(
        select(Message.conversation_id, Message.direction, Message.created_at)
        .where(Message.tenant_id == tenant_id, Message.created_at >= since)
        .order_by(Message.conversation_id, Message.created_at)
        .limit(2000)
    )
    rows = result.all()
    pending: dict[uuid.UUID, datetime] = {}
    deltas: list[float] = []
    for conv_id, direction, created in rows:
        dir_val = direction.value if hasattr(direction, "value") else direction
        if dir_val == "inbound":
            pending[conv_id] = created
        elif dir_val == "outbound" and conv_id in pending:
            deltas.append((created - pending.pop(conv_id)).total_seconds() / 60)
    if not deltas:
        return 0.0
    return round(sum(deltas) / len(deltas), 1)


async def get_costs(db: AsyncSession, tenant_id: uuid.UUID, period: str = "30d") -> CostBreakdown:
    days = _period_days(period)
    period_start = datetime.now(tz=timezone.utc) - timedelta(days=days)
    tokens_res = await db.execute(
        select(func.coalesce(func.sum(Message.tokens_used), 0)).where(
            Message.tenant_id == tenant_id,
            Message.direction == MessageDirection.OUTBOUND,
            Message.created_at >= period_start,
        )
    )
    tokens = int(tokens_res.scalar() or 0)
    calls_res = await db.execute(
        select(func.count(Call.id), func.coalesce(func.sum(Call.duration_seconds), 0)).where(
            Call.tenant_id == tenant_id, Call.created_at >= period_start
        )
    )
    row = calls_res.one()
    calls_count = int(row[0] or 0)
    call_seconds = int(row[1] or 0)

    claude_usd = round(tokens / 1_000_000 * settings.CLAUDE_USD_PER_MTOK, 2)
    retell_usd = round(call_seconds / 60 * 0.07, 2)
    twilio_usd = round(call_seconds / 60 * 0.014, 2)
    fal_usd = 0.0
    total = round(claude_usd + retell_usd + twilio_usd + fal_usd, 2)
    return CostBreakdown(
        claude_usd=claude_usd,
        twilio_usd=twilio_usd,
        retell_usd=retell_usd,
        fal_usd=fal_usd,
        total_usd=total,
        tokens_used=tokens,
        calls_count=calls_count,
    )
