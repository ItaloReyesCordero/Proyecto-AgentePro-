from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    admin,
    agent,
    appointments,
    automations,
    auth,
    calls,
    contacts,
    conversations,
    instagram,
    metrics,
    notion,
    provisioning,
    subscriptions,
    tenants,
    voice,
    whatsapp,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(conversations.router)
api_router.include_router(contacts.router)
api_router.include_router(calls.router)
api_router.include_router(instagram.router)
api_router.include_router(automations.router)
api_router.include_router(agent.router)
api_router.include_router(appointments.router)
api_router.include_router(voice.router)
api_router.include_router(whatsapp.router)
api_router.include_router(notion.router)
api_router.include_router(metrics.router)
api_router.include_router(subscriptions.router)
api_router.include_router(provisioning.router)
api_router.include_router(admin.router)
