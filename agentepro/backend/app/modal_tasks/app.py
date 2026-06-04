from __future__ import annotations

import modal

app = modal.App("agentepro-tasks")

# Imagen con todas las dependencias necesarias para las automatizaciones.
# El código de `app/` se monta para reutilizar modelos y servicios.
image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install(
        "anthropic>=0.40.0",
        "httpx>=0.27.0",
        "sqlalchemy[asyncio]>=2.0.0",
        "asyncpg>=0.29.0",
        "retell-sdk>=4.0.0",
        "twilio>=9.0.0",
        "hubspot-api-client>=10.0.0",
        "resend>=2.0.0",
        "structlog>=24.2.0",
        "pydantic>=2.7.0",
        "pydantic-settings>=2.3.0",
        "phonenumbers>=8.13.0",
        "cryptography>=42.0.0",
        "python-socketio>=5.11.0",
        "email-validator>=2.2.0",
        "fal-client>=0.5.0",
        "openai>=1.40.0",
    )
    .add_local_dir("app", remote_path="/root/app")
)

# Los secretos (DATABASE_URL, ANTHROPIC_API_KEY, etc.) se inyectan desde Modal.
secrets = [modal.Secret.from_name("agentepro-secrets")]
