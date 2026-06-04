from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call import Call, CallDirection, CallStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_call_by_retell_id(db: AsyncSession, retell_call_id: str) -> Call | None:
    result = await db.execute(select(Call).where(Call.retell_call_id == retell_call_id))
    return result.scalar_one_or_none()


async def create_call(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    retell_call_id: str | None = None,
    twilio_call_sid: str | None = None,
    direction: str = "inbound",
    from_number: str | None = None,
    to_number: str | None = None,
    contact_id: uuid.UUID | None = None,
    status: CallStatus = CallStatus.INITIATED,
) -> Call:
    call = Call(
        tenant_id=tenant_id,
        retell_call_id=retell_call_id,
        twilio_call_sid=twilio_call_sid,
        direction=CallDirection(direction),
        from_number=from_number,
        to_number=to_number,
        contact_id=contact_id,
        status=status,
        started_at=datetime.now(tz=timezone.utc),
    )
    db.add(call)
    await db.flush()
    return call
