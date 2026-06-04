"""Utilidades compartidas por los tests de integración HTTP.

Se apoyan en el fixture ``client`` (definido en conftest) y en
``AsyncSessionLocal`` para sembrar datos directamente cuando no hay endpoint
de alta (p. ej. los contactos nacen de los webhooks, no de un POST del panel).
"""
from __future__ import annotations

import uuid
from typing import Any

from httpx import AsyncClient

API = "/api/v1"


def bearer(token: str) -> dict[str, str]:
    """Cabecera Authorization Bearer para el dueño autenticado."""
    return {"Authorization": f"Bearer {token}"}


async def register(
    client: AsyncClient,
    email: str = "owner@example.com",
    password: str = "Secret123",
    business: str = "Negocio Test",
    business_type: str = "services",
    full_name: str = "Dueño Test",
):
    """Registra un negocio + dueño. Devuelve la respuesta cruda."""
    return await client.post(
        f"{API}/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "business_name": business,
            "business_type": business_type,
        },
    )


async def register_and_auth(client: AsyncClient, **kwargs) -> tuple[str, dict[str, str], dict[str, Any]]:
    """Registra y devuelve (token, cabecera_bearer, cuerpo_json)."""
    r = await register(client, **kwargs)
    assert r.status_code == 201, r.text
    body = r.json()
    token = body["access_token"]
    return token, bearer(token), body


async def tenant_id_of(body: dict[str, Any]) -> str:
    """Extrae el tenant_id del cuerpo de registro/login."""
    return body["user"]["tenant_id"]


async def set_plan(tenant_id: str, plan: str) -> None:
    """Cambia el plan de un tenant directamente en la BD (los tests nacen TRIAL).

    Útil para probar módulos gateados por plan (p. ej. Automatizaciones es solo
    de Enterprise)."""
    from app.database import AsyncSessionLocal
    from app.models.tenant import PlanType, Tenant

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, uuid.UUID(str(tenant_id)))
        tenant.plan = PlanType(plan)
        await db.commit()


async def seed_contact(tenant_id: str, **kwargs) -> str:
    """Crea un contacto directamente en la BD y devuelve su id (str)."""
    from app.database import AsyncSessionLocal
    from app.models.contact import Contact

    async with AsyncSessionLocal() as db:
        contact = Contact(
            tenant_id=uuid.UUID(str(tenant_id)),
            full_name=kwargs.get("full_name", "Cliente Demo"),
            phone_number=kwargs.get("phone_number", "+51999111222"),
            wa_id=kwargs.get("wa_id", "51999111222"),
            email=kwargs.get("email"),
            qualification_score=kwargs.get("qualification_score", 0),
            total_messages=kwargs.get("total_messages", 0),
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return str(contact.id)


async def seed_conversation(tenant_id: str, contact_id: str, **kwargs) -> str:
    """Crea una conversación directamente en la BD y devuelve su id (str)."""
    from app.database import AsyncSessionLocal
    from app.models.conversation import Conversation

    async with AsyncSessionLocal() as db:
        conv = Conversation(
            tenant_id=uuid.UUID(str(tenant_id)),
            contact_id=uuid.UUID(str(contact_id)),
            subject=kwargs.get("subject", "Consulta"),
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return str(conv.id)
