from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.conversation import (
    Conversation,
    ConversationAssigneeType,
    ConversationChannel,
    ConversationStatus,
)
from app.models.message import Message, MessageDirection, MessageType, SenderType
from app.utils.logger import get_logger

logger = get_logger(__name__)

_OPEN_STATES = (ConversationStatus.OPEN, ConversationStatus.IN_PROGRESS, ConversationStatus.WAITING)


async def get_or_create_open_conversation(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    contact: Contact,
    channel: str = "whatsapp",
) -> Conversation:
    """Devuelve la conversación abierta del contacto o crea una nueva."""
    channel_enum = {
        "whatsapp": ConversationChannel.WHATSAPP,
        "instagram": ConversationChannel.INSTAGRAM,
        "instagram_dm": ConversationChannel.INSTAGRAM,
        "voice": ConversationChannel.VOICE,
    }.get(channel, ConversationChannel.WHATSAPP)

    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.contact_id == contact.id,
            Conversation.channel == channel_enum,
            Conversation.status.in_(_OPEN_STATES),
        )
        .order_by(Conversation.last_message_at.desc())
    )
    conv = result.scalars().first()
    if conv is not None:
        return conv

    now = datetime.now(tz=timezone.utc)
    conv = Conversation(
        tenant_id=tenant_id,
        contact_id=contact.id,
        channel=channel_enum,
        status=ConversationStatus.OPEN,
        assignee_type=ConversationAssigneeType.AI,
        first_message_at=now,
        last_message_at=now,
    )
    db.add(conv)
    await db.flush()
    contact.total_conversations = (contact.total_conversations or 0) + 1
    logger.info("conversation_created", conversation_id=str(conv.id))
    return conv


async def find_message_by_wa_id(db: AsyncSession, wa_message_id: str) -> Message | None:
    result = await db.execute(select(Message).where(Message.wa_message_id == wa_message_id))
    return result.scalar_one_or_none()


async def save_message(
    db: AsyncSession,
    *,
    conversation: Conversation,
    tenant_id: uuid.UUID,
    direction: MessageDirection,
    sender_type: SenderType,
    content: str,
    message_type: MessageType = MessageType.TEXT,
    wa_message_id: str | None = None,
    media_url: str | None = None,
    transcription: str | None = None,
    tokens_used: int = 0,
) -> Message:
    """Persiste un mensaje y actualiza contadores de la conversación."""
    now = datetime.now(tz=timezone.utc)
    message = Message(
        conversation_id=conversation.id,
        tenant_id=tenant_id,
        wa_message_id=wa_message_id,
        direction=direction,
        message_type=message_type,
        sender_type=sender_type,
        content=content,
        media_url=media_url,
        transcription=transcription,
        tokens_used=tokens_used,
        is_read=direction == MessageDirection.OUTBOUND,
    )
    db.add(message)
    conversation.message_count = (conversation.message_count or 0) + 1
    conversation.last_message_at = now
    conversation.tokens_used = (conversation.tokens_used or 0) + tokens_used
    if direction == MessageDirection.INBOUND:
        conversation.unread_count = (conversation.unread_count or 0) + 1
    await db.flush()
    return message


def is_bot_active(conversation: Conversation) -> bool:
    """El bot responde solo si la conversación está asignada a la IA y abierta."""
    return (
        conversation.assignee_type == ConversationAssigneeType.AI
        and conversation.status in _OPEN_STATES
    )


async def takeover(db: AsyncSession, conversation: Conversation) -> None:
    conversation.assignee_type = ConversationAssigneeType.HUMAN
    conversation.status = ConversationStatus.IN_PROGRESS
    await db.flush()


async def release(db: AsyncSession, conversation: Conversation) -> None:
    conversation.assignee_type = ConversationAssigneeType.AI
    conversation.status = ConversationStatus.OPEN
    await db.flush()


async def escalate(db: AsyncSession, conversation: Conversation) -> None:
    conversation.status = ConversationStatus.ESCALATED
    conversation.assignee_type = ConversationAssigneeType.HUMAN
    await db.flush()
