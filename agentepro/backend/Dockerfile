# AgentePro 2.0 — Backend (FastAPI + Socket.io)
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# uv como gestor de dependencias (instala rápido en el entorno del sistema)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Instala dependencias primero (cache de capas). Se listan explícitamente para
# no depender de un build-system del proyecto.
RUN uv pip install --system --no-cache \
    "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "sqlalchemy[asyncio]>=2.0.0" \
    "asyncpg>=0.29.0" "psycopg2-binary>=2.9.0" "alembic>=1.13.0" "pydantic>=2.7.0" "pydantic-settings>=2.3.0" \
    "anthropic>=0.40.0" "httpx>=0.27.0" "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" "bcrypt==4.0.1" "python-multipart>=0.0.9" "redis>=5.0.0" "celery>=5.4.0" \
    "structlog>=24.2.0" "python-dotenv>=1.0.0" "email-validator>=2.2.0" \
    "phonenumbers>=8.13.0" "cryptography>=42.0.0" "python-socketio>=5.11.0" \
    "retell-sdk>=4.0.0" "twilio>=9.0.0" "hubspot-api-client>=10.0.0" \
    "modal>=0.63.0" "resend>=2.0.0" "fal-client>=0.5.0" "tzdata>=2024.1" \
    "aiosqlite>=0.20.0" "pytest>=8.2.0" "pytest-asyncio>=0.23.0" "pytest-cov>=5.0.0"

# Copia el código
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:socket_app --host 0.0.0.0 --port ${PORT:-8000}"]
