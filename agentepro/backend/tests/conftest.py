from __future__ import annotations

import os

# Configura entorno de pruebas ANTES de importar la app (database.py crea el
# engine al importar). Se FUERZAN los valores (no setdefault) para que las
# pruebas sean herméticas aunque se corran dentro del contenedor (cuyo .env trae
# Postgres y META_APP_SECRET vacío): usamos SQLite async, secretos de test y
# rate-limit desactivado (si no, varios logins seguidos darían 429).
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["META_APP_SECRET"] = "test-app-secret"
os.environ["ADMIN_SECRET_KEY"] = "test-admin-key"
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["DEBUG"] = "false"  # silencia el echo SQL en los tests
# El webhook de Retell omite la firma cuando no hay secreto: lo forzamos vacío
# para que los tests no dependan del .env local del desarrollador.
os.environ["RETELL_WEBHOOK_SECRET"] = ""
# Sin credenciales de Twilio en tests: evita que el envío "fallback" a Twilio
# mande mensajes REALES durante las pruebas (deben ser herméticas).
os.environ["TWILIO_ACCOUNT_SID"] = ""
os.environ["TWILIO_AUTH_TOKEN"] = ""

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

#: Header para autenticarse como plataforma/superadmin en los tests de admin.
ADMIN_HEADERS = {"X-Admin-Key": "test-admin-key"}


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Cliente HTTP contra la app real con una BD SQLite limpia por test.

    Crea las tablas antes y las borra después, todo en el MISMO event loop que
    las peticiones (por eso httpx + ASGITransport en vez de TestClient): así
    aiosqlite no se queja de "loop distinto".
    """
    from app.database import Base, engine
    import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
