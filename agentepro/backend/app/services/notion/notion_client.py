from __future__ import annotations

from typing import Any

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Nombres de propiedad aceptados (en minúsculas) para mapear cada campo del
# catálogo. La propiedad de tipo "title" siempre se usa como nombre si no se
# encontró otra. Es flexible a propósito: el dueño arma su Notion como quiera.
_PRICE_KEYS = {"precio", "price", "costo", "cost", "tarifa", "monto"}
_DESCRIPTION_KEYS = {"descripcion", "descripción", "description", "detalle", "detalles", "nota", "notas"}
_CATEGORY_KEYS = {"categoria", "categoría", "category", "tipo", "rubro"}
_NAME_KEYS = {"nombre", "name", "servicio", "producto", "titulo", "título", "item"}


class NotionError(Exception):
    """Error al comunicarse con la API de Notion (token o base inválidos)."""


def _plain_text(prop: dict[str, Any]) -> str:
    """Extrae texto plano de una propiedad de Notion sin importar su tipo."""
    if not isinstance(prop, dict):
        return ""
    ptype = prop.get("type")
    value = prop.get(ptype) if ptype else None

    if ptype in ("title", "rich_text") and isinstance(value, list):
        return "".join(part.get("plain_text", "") for part in value).strip()
    if ptype == "number" and value is not None:
        # Entero si no tiene decimales (evita "25.0").
        return str(int(value)) if float(value).is_integer() else str(value)
    if ptype == "select" and isinstance(value, dict):
        return (value.get("name") or "").strip()
    if ptype == "multi_select" and isinstance(value, list):
        return ", ".join(opt.get("name", "") for opt in value).strip()
    if ptype in ("phone_number", "email", "url") and isinstance(value, str):
        return value.strip()
    if ptype == "checkbox":
        return "Sí" if value else "No"
    if ptype == "status" and isinstance(value, dict):
        return (value.get("name") or "").strip()
    if ptype == "date" and isinstance(value, dict):
        return (value.get("start") or "").strip()
    return ""


def _row_to_service(properties: dict[str, Any]) -> dict[str, Any] | None:
    """Convierte una fila de Notion en {name, description, price, category}.

    Devuelve None si la fila no tiene nombre (fila vacía)."""
    name = ""
    description = ""
    price = ""
    category = ""

    # Primer paso: ubica la propiedad de tipo "title" como nombre por defecto.
    for prop in properties.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            name = _plain_text(prop)
            break

    # Segundo paso: mapea por nombre de columna (case-insensitive).
    for raw_key, prop in properties.items():
        key = raw_key.strip().lower()
        text = _plain_text(prop)
        if not text:
            continue
        if key in _PRICE_KEYS and not price:
            price = text
        elif key in _DESCRIPTION_KEYS and not description:
            description = text
        elif key in _CATEGORY_KEYS and not category:
            category = text
        elif key in _NAME_KEYS and not name:
            name = text

    if not name:
        return None
    return {"name": name, "description": description, "price": price, "category": category}


async def _query_database(
    client: httpx.AsyncClient, headers: dict[str, str], database_id: str
) -> list[dict[str, Any]] | None:
    """Consulta una base de datos de Notion y devuelve los servicios.

    Devuelve ``None`` (señal, no error) si el ID resultó ser una PÁGINA en vez de
    una base de datos: el llamador intentará ubicar la tabla dentro de esa página.
    """
    services: list[dict[str, Any]] = []
    payload: dict[str, Any] = {"page_size": 100}
    while True:
        resp = await client.post(
            f"/databases/{database_id}/query", headers=headers, json=payload
        )
        if resp.status_code == 401:
            raise NotionError("Token de Notion inválido o sin permisos sobre la base.")
        if resp.status_code == 404:
            raise NotionError("No se encontró la base de datos (revisa el ID y compártela con la integración).")
        if resp.status_code == 400:
            message = ""
            try:
                message = resp.json().get("message", "")
            except Exception:
                message = resp.text
            if "is a page" in message or "not a database" in message:
                return None  # es una página: el llamador buscará la tabla dentro
            raise NotionError(f"Notion respondió 400: {message[:200]}")
        if resp.status_code >= 400:
            raise NotionError(f"Notion respondió {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        for row in data.get("results", []):
            svc = _row_to_service(row.get("properties", {}))
            if svc:
                services.append(svc)
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data.get("next_cursor")
    return services


async def _find_child_database_id(
    client: httpx.AsyncClient, headers: dict[str, str], page_id: str
) -> str | None:
    """Busca dentro de una página de Notion el primer bloque que sea una tabla
    (``child_database``) y devuelve su ID. None si no hay ninguna."""
    cursor: str | None = None
    while True:
        params: dict[str, Any] = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        resp = await client.get(
            f"/blocks/{page_id}/children", headers=headers, params=params
        )
        if resp.status_code >= 400:
            return None
        data = resp.json()
        for block in data.get("results", []):
            if block.get("type") == "child_database":
                return block.get("id")
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return None


async def fetch_catalog(api_key: str, database_id: str) -> list[dict[str, Any]]:
    """Lee TODAS las filas de una base de datos de Notion y las devuelve como
    lista de servicios ``[{name, description, price, category}]``.

    Es tolerante: si el usuario pega el enlace de una PÁGINA que contiene una
    tabla, ubica esa tabla automáticamente. Lanza :class:`NotionError` si el
    token es inválido o no hay una tabla accesible.
    """
    if not api_key or not database_id:
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(base_url=NOTION_API_BASE, timeout=20.0) as client:
        try:
            services = await _query_database(client, headers, database_id)
            if services is None:
                # El ID era una página: busca una tabla (base de datos) dentro.
                child_id = await _find_child_database_id(client, headers, database_id)
                if not child_id:
                    raise NotionError(
                        "El enlace es de una PÁGINA de Notion, no de una tabla, y no "
                        "encontré ninguna tabla dentro. Crea una tabla (base de datos) "
                        "en esa página y compártela con la integración, o pega el enlace "
                        "de la tabla."
                    )
                services = await _query_database(client, headers, child_id)
                if services is None:
                    raise NotionError("No pude leer la tabla dentro de la página de Notion.")
        except httpx.HTTPError as exc:  # red caída, timeout, etc.
            raise NotionError(f"No se pudo conectar con Notion: {exc}") from exc

    logger.info("notion_catalog_fetched", count=len(services))
    return services
