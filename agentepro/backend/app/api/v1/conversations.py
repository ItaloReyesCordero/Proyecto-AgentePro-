from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.dependencies import CurrentTenant, DbSession
from app.models.contact import Contact
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageDirection, MessageType, SenderType
from app.models.tenant import Tenant
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.conversation import ConversationOut, ConversationUpdate
from app.schemas.message import MessageOut, SendMessageRequest
from app.services import conversation_service
from app.services.contact_service import apply_lead_update
from app.services.whatsapp.sender import send_whatsapp_message

router = APIRouter(prefix="/conversations", tags=["conversations"])


async def _serialize(db: DbSession, conv: Conversation) -> ConversationOut:
    contact = await db.get(Contact, conv.contact_id)
    last_msg_res = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    last_msg = last_msg_res.scalar_one_or_none()
    return ConversationOut.from_model(
        conv, contact, MessageOut.from_model(last_msg) if last_msg else None
    )


async def _get_owned(db: DbSession, tenant: Tenant, conversation_id: uuid.UUID) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.tenant_id == tenant.id
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("", response_model=PaginatedResponse[ConversationOut])
async def list_conversations(
    tenant: CurrentTenant,
    db: DbSession,
    status_filter: str | None = Query(None, alias="status"),
    channel: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ConversationOut]:
    conditions = [Conversation.tenant_id == tenant.id]
    if channel:
        ch = "instagram" if channel == "instagram_dm" else channel
        conditions.append(Conversation.channel == ch)

    total_res = await db.execute(select(func.count(Conversation.id)).where(*conditions))
    total = int(total_res.scalar() or 0)

    result = await db.execute(
        select(Conversation)
        .where(*conditions)
        .order_by(Conversation.last_message_at.desc().nullslast())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    convs = list(result.scalars().all())
    items = [await _serialize(db, c) for c in convs]
    return PaginatedResponse.build(items, total, page, per_page)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> ConversationOut:
    conv = await _get_owned(db, tenant, conversation_id)
    return await _serialize(db, conv)


@router.get("/{conversation_id}/messages", response_model=PaginatedResponse[MessageOut])
async def list_messages(
    conversation_id: uuid.UUID,
    tenant: CurrentTenant,
    db: DbSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
) -> PaginatedResponse[MessageOut]:
    await _get_owned(db, tenant, conversation_id)
    total_res = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    total = int(total_res.scalar() or 0)
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    items = [MessageOut.from_model(m) for m in result.scalars().all()]
    return PaginatedResponse.build(items, total, page, per_page)


@router.post("/{conversation_id}/takeover", response_model=MessageResponse)
async def takeover(conversation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> MessageResponse:
    conv = await _get_owned(db, tenant, conversation_id)
    await conversation_service.takeover(db, conv)
    return MessageResponse(message="Control tomado por humano")


@router.post("/{conversation_id}/release", response_model=MessageResponse)
async def release(conversation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> MessageResponse:
    conv = await _get_owned(db, tenant, conversation_id)
    await conversation_service.release(db, conv)
    return MessageResponse(message="Conversación devuelta a la IA")


@router.post("/{conversation_id}/close", response_model=MessageResponse)
async def close_conversation(
    conversation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> MessageResponse:
    conv = await _get_owned(db, tenant, conversation_id)
    conv.status = ConversationStatus.CLOSED
    await db.flush()
    return MessageResponse(message="Conversación cerrada")


@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    tenant: CurrentTenant,
    db: DbSession,
) -> MessageOut:
    """Envía un mensaje manual (modo humano) y lo persiste."""
    conv = await _get_owned(db, tenant, conversation_id)
    contact = await db.get(Contact, conv.contact_id)
    if contact and (contact.wa_id or contact.phone_number):
        await send_whatsapp_message(tenant, contact.wa_id or contact.phone_number, payload.content)
    message = await conversation_service.save_message(
        db,
        conversation=conv,
        tenant_id=tenant.id,
        direction=MessageDirection.OUTBOUND,
        sender_type=SenderType.HUMAN,
        content=payload.content,
        message_type=MessageType.TEXT,
    )
    return MessageOut.from_model(message)


@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    tenant: CurrentTenant,
    db: DbSession,
) -> ConversationOut:
    conv = await _get_owned(db, tenant, conversation_id)
    if payload.tags is not None:
        conv.tags = payload.tags
    if payload.lead_stage:
        contact = await db.get(Contact, conv.contact_id)
        if contact:
            apply_lead_update(contact, contact.qualification_score, payload.lead_stage)
    await db.flush()
    return await _serialize(db, conv)


@router.post("/{conversation_id}/pause-bot", response_model=MessageResponse)
async def pause_bot(conversation_id: uuid.UUID, tenant: CurrentTenant, db: DbSession) -> MessageResponse:
    conv = await _get_owned(db, tenant, conversation_id)
    await conversation_service.takeover(db, conv)
    return MessageResponse(message="Bot pausado")
