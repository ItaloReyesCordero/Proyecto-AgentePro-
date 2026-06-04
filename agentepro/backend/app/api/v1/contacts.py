from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select

from app.core.plans import FEATURE_CONTACTS
from app.dependencies import CurrentTenant, DbSession, require_feature
from app.models.call import Call
from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.tenant import Tenant
from app.schemas.call import CallOut
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.contact import ContactOut, ContactUpdate
from app.schemas.conversation import ConversationOut
from app.schemas.message import SendMessageRequest
from app.services.contact_service import apply_lead_update, get_contact
from app.services.voice.outbound_caller import OutboundCallError, call_lead
from app.services.whatsapp.sender import send_whatsapp_message

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
    dependencies=[Depends(require_feature(FEATURE_CONTACTS))],
)


async def _require(db: DbSession, tenant: Tenant, contact_id: uuid.UUID) -> Contact:
    contact = await get_contact(db, tenant.id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("", response_model=PaginatedResponse[ContactOut])
async def list_contacts(
    tenant: CurrentTenant,
    db: DbSession,
    search: str | None = None,
    lead_stage: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ContactOut]:
    conditions = [Contact.tenant_id == tenant.id]
    if search:
        like = f"%{search}%"
        conditions.append(
            or_(Contact.full_name.ilike(like), Contact.phone_number.ilike(like))
        )
    total_res = await db.execute(select(func.count(Contact.id)).where(*conditions))
    total = int(total_res.scalar() or 0)
    result = await db.execute(
        select(Contact)
        .where(*conditions)
        .order_by(Contact.last_interaction_at.desc().nullslast())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    items = [ContactOut.from_model(c) for c in result.scalars().all()]
    return PaginatedResponse.build(items, total, page, per_page)


@router.get("/{contact_id}", response_model=ContactOut)
async def get_contact_detail(
    contact_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> ContactOut:
    return ContactOut.from_model(await _require(db, tenant, contact_id))


@router.patch("/{contact_id}", response_model=ContactOut)
async def update_contact(
    contact_id: uuid.UUID, payload: ContactUpdate, tenant: CurrentTenant, db: DbSession
) -> ContactOut:
    contact = await _require(db, tenant, contact_id)
    if payload.name is not None:
        contact.full_name = payload.name
    if payload.email is not None:
        contact.email = payload.email
    if payload.tags is not None:
        contact.tags = payload.tags
    if payload.notes is not None:
        contact.notes = payload.notes
    if payload.lead_stage:
        apply_lead_update(contact, contact.qualification_score, payload.lead_stage)
    await db.flush()
    return ContactOut.from_model(contact)


@router.get("/{contact_id}/conversations", response_model=list[ConversationOut])
async def contact_conversations(
    contact_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> list[ConversationOut]:
    contact = await _require(db, tenant, contact_id)
    result = await db.execute(
        select(Conversation)
        .where(Conversation.contact_id == contact.id)
        .order_by(Conversation.last_message_at.desc().nullslast())
    )
    return [ConversationOut.from_model(c, contact) for c in result.scalars().all()]


@router.get("/{contact_id}/calls", response_model=list[CallOut])
async def contact_calls(
    contact_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> list[CallOut]:
    contact = await _require(db, tenant, contact_id)
    result = await db.execute(
        select(Call).where(Call.contact_id == contact.id).order_by(Call.created_at.desc())
    )
    return [CallOut.from_model(c, contact) for c in result.scalars().all()]


@router.post("/{contact_id}/do-not-contact", response_model=MessageResponse)
async def do_not_contact(
    contact_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> MessageResponse:
    contact = await _require(db, tenant, contact_id)
    contact.opted_in = False
    await db.flush()
    return MessageResponse(message="Contacto marcado como 'no contactar'")


@router.post("/{contact_id}/call", response_model=MessageResponse)
async def call_contact(
    contact_id: uuid.UUID, tenant: CurrentTenant, db: DbSession
) -> MessageResponse:
    contact = await _require(db, tenant, contact_id)
    try:
        await call_lead(db, tenant, contact, reason="manual")
    except OutboundCallError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MessageResponse(message="Llamada iniciada")


@router.post("/{contact_id}/send-whatsapp", response_model=MessageResponse)
async def send_whatsapp_to_contact(
    contact_id: uuid.UUID,
    payload: SendMessageRequest,
    tenant: CurrentTenant,
    db: DbSession,
) -> MessageResponse:
    contact = await _require(db, tenant, contact_id)
    to = contact.wa_id or contact.phone_number
    if not to:
        raise HTTPException(status_code=400, detail="Contact has no phone")
    ok = await send_whatsapp_message(tenant, to, payload.content)
    return MessageResponse(success=ok, message="Mensaje enviado" if ok else "Falló el envío")
