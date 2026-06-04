from __future__ import annotations

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware, TenantMiddleware
from app.core.socket import sio
from app.database import engine
from app.utils.logger import get_logger, setup_logging
from app.webhooks import culqi, meta_instagram, meta_whatsapp, retell, twilio_voice, twilio_whatsapp

setup_logging(debug=settings.DEBUG)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("startup", app=settings.APP_NAME, version=settings.VERSION)
    # Verifica conexión a la base de datos (best-effort, no bloquea el arranque).
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("database_connection_ok")
    except Exception as exc:
        logger.error("database_connection_failed", error=str(exc))

    if not settings.ANTHROPIC_API_KEY:
        logger.warning("anthropic_api_key_missing")

    # Siembra la cuenta de super admin del fundador si aún no existe.
    try:
        from app.core.seed import seed_superadmin

        await seed_superadmin()
    except Exception as exc:
        logger.error("superadmin_seed_failed", error=str(exc))

    yield
    logger.info("shutdown", app=settings.APP_NAME)
    await engine.dispose()


app = FastAPI(
    title="AgentePro API",
    version=settings.VERSION,
    description="SaaS de automatización de negocios con IA",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
setup_exception_handlers(app)

# REST API
app.include_router(api_router, prefix="/api/v1")

# Webhooks (each module mounts its own /webhooks/... paths)
app.include_router(meta_whatsapp.router, prefix="/webhooks")
app.include_router(meta_instagram.router, prefix="/webhooks")
app.include_router(retell.router, prefix="/webhooks")
app.include_router(twilio_voice.router, prefix="/webhooks")
app.include_router(twilio_whatsapp.router, prefix="/webhooks")
app.include_router(culqi.router, prefix="/webhooks")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.VERSION}


# ---------------------------------------------------------------------------
# Servir el frontend (SPA) desde el mismo proceso, SOLO si existe la carpeta
# compilada (la define FRONTEND_DIST_DIR en la imagen "todo en uno", p. ej. en
# Railway). En desarrollo (Docker) el front lo sirve Vite, así que esto se omite
# y no afecta nada. Al ser el MISMO origen, no hay problemas de CORS ni de URLs.
# ---------------------------------------------------------------------------
# Por defecto busca /app/frontend_dist (donde lo deja la imagen "todo en uno").
# Si no existe (p. ej. en el contenedor de desarrollo, que sólo tiene el backend),
# simplemente no se activa y Vite sigue sirviendo el front por separado.
_FRONTEND_DIST = os.environ.get("FRONTEND_DIST_DIR", "").strip() or "/app/frontend_dist"
if os.path.isdir(_FRONTEND_DIST):
    _assets_dir = os.path.join(_FRONTEND_DIST, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    _NON_SPA_PREFIXES = (
        "api/", "webhooks/", "health", "socket.io", "docs", "redoc", "openapi.json",
    )
    _dist_root = os.path.realpath(_FRONTEND_DIST)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        """Sirve los archivos estáticos del build y, para cualquier ruta del SPA
        (p. ej. /app, /login, /privacidad), devuelve index.html (fallback)."""
        if full_path.startswith(_NON_SPA_PREFIXES):
            raise HTTPException(status_code=404, detail="Not found")
        # Evita path traversal: el archivo debe quedar dentro de la carpeta dist.
        candidate = os.path.realpath(os.path.join(_FRONTEND_DIST, full_path))
        if (
            full_path
            and candidate.startswith(_dist_root + os.sep)
            and os.path.isfile(candidate)
        ):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))

    logger.info("frontend_static_serving_enabled", dir=_FRONTEND_DIST)


# ASGI app combinando FastAPI + Socket.io
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
