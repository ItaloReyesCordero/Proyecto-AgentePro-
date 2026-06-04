from __future__ import annotations
import time
from typing import Callable, Awaitable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.core.rate_limit import FixedWindowLimiter
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Rutas sensibles a fuerza bruta y su límite por minuto y por IP.
_RATE_LIMITED_PATHS: dict[str, int] = {
    "/api/v1/auth/login": 5,
    "/api/v1/auth/register": 5,
    "/api/v1/signup": 5,
    "/api/v1/auth/password-reset-request": 5,
}

_redis_client = None

# Fallback en memoria (por proceso) cuando Redis no está disponible: así las
# rutas sensibles NO quedan sin límite. Un limitador por ruta, ventana de 60s.
_fallback_limiters: dict[str, FixedWindowLimiter] = {}


def _fallback_blocked(path: str, limit: int, ip: str) -> bool:
    limiter = _fallback_limiters.get(path)
    if limiter is None:
        limiter = _fallback_limiters[path] = FixedWindowLimiter(limit, 60)
    return not limiter.allow(f"{path}:{ip}")


def _get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis

            _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as exc:  # pragma: no cover
            logger.warning("redis_unavailable_for_ratelimit", error=str(exc))
            _redis_client = False  # marca "no disponible"
    return _redis_client or None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            "request_processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting por IP en rutas sensibles (login/registro/signup) usando
    una ventana fija de 60s en Redis. Si Redis no está disponible, deja pasar."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        limit = _RATE_LIMITED_PATHS.get(request.url.path)
        if limit and request.method == "POST" and settings.RATE_LIMIT_ENABLED:
            ip = request.client.host if request.client else "unknown"
            redis = _get_redis()
            blocked = False
            if redis is not None:
                key = f"ratelimit:{request.url.path}:{ip}"
                try:
                    count = await redis.incr(key)
                    if count == 1:
                        await redis.expire(key, 60)
                    blocked = count > limit
                except Exception as exc:  # pragma: no cover
                    logger.warning("ratelimit_redis_error", error=str(exc))
                    # Redis falló a mitad: usa el fallback en memoria.
                    blocked = _fallback_blocked(request.url.path, limit, ip)
            else:
                # Sin Redis: no quedamos "fail-open", limitamos en memoria.
                blocked = _fallback_blocked(request.url.path, limit, ip)

            if blocked:
                logger.warning("rate_limited", path=request.url.path, ip=ip)
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Demasiados intentos. Espera un minuto.",
                        "error": "RateLimited",
                    },
                )
        return await call_next(request)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware que extrae el tenant del header X-Tenant-Slug o del token JWT
    y lo agrega al estado del request para uso en los handlers.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        tenant_slug = request.headers.get("X-Tenant-Slug")
        if tenant_slug:
            request.state.tenant_slug = tenant_slug
        return await call_next(request)
