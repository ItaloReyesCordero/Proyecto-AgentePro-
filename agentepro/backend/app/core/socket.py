from __future__ import annotations

from typing import Any

import socketio

from app.config import settings
from app.core.security import decode_token
from app.utils.logger import get_logger

logger = get_logger(__name__)

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[settings.FRONTEND_URL],
    logger=False,
    engineio_logger=False,
)


def _tenant_room(tenant_id: str) -> str:
    return f"tenant:{tenant_id}"


@sio.event
async def connect(sid: str, environ: dict[str, Any], auth: dict[str, Any] | None) -> bool:
    """Autentica el socket con el JWT y lo une a la room de su tenant."""
    token = (auth or {}).get("token")
    if not token:
        logger.warning("socket_connect_no_token", sid=sid)
        return False
    try:
        payload = decode_token(token)
    except Exception:
        logger.warning("socket_connect_invalid_token", sid=sid)
        return False

    tenant_id = payload.get("tenant_id")
    if tenant_id:
        await sio.enter_room(sid, _tenant_room(str(tenant_id)))
        await sio.save_session(sid, {"tenant_id": str(tenant_id), "user_id": payload.get("sub")})
    logger.info("socket_connected", sid=sid, tenant_id=tenant_id)
    return True


@sio.event
async def disconnect(sid: str) -> None:
    logger.info("socket_disconnected", sid=sid)


@sio.on("join_tenant")
async def join_tenant(sid: str, data: dict[str, Any]) -> None:
    tenant_id = data.get("tenant_id")
    if tenant_id:
        await sio.enter_room(sid, _tenant_room(str(tenant_id)))


async def emit_to_tenant(tenant_id: str, event: str, data: dict[str, Any]) -> None:
    """Emite un evento a todos los sockets de un tenant. Seguro ante fallos."""
    try:
        await sio.emit(event, data, room=_tenant_room(str(tenant_id)))
    except Exception as exc:  # pragma: no cover - emisión best-effort
        logger.error("socket_emit_error", event=event, error=str(exc))
