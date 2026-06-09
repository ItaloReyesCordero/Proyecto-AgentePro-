from __future__ import annotations

import os

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    """Construye la DATABASE_URL por defecto a partir de componentes del entorno.

    No incrusta credenciales en el código fuente: usuario/clave/host/puerto/db se
    leen de variables de entorno (las mismas que define docker-compose para el
    contenedor de Postgres en desarrollo). En PRODUCCIÓN (Railway) se define
    DATABASE_URL directamente y este default ni se usa. En tests, conftest fuerza
    una URL de SQLite antes de importar la app.
    """
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "agentepro")
    auth = f"{user}:{password}@" if password else f"{user}@"
    return f"postgresql+asyncpg://{auth}{host}:{port}/{db}"


class Settings(BaseSettings):
    APP_NAME: str = "AgentePro"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    # IMPORTANTE: en PRODUCCIÓN estos secretos DEBEN venir por variable de entorno
    # (SECRET_KEY, ADMIN_SECRET_KEY). El fallback de abajo es solo para arrancar en
    # desarrollo local y NO debe usarse en producción.
    SECRET_KEY: str = Field(default_factory=lambda: os.environ.get("SECRET_KEY", "local-dev-only-change-me"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ADMIN_SECRET_KEY: str = Field(default_factory=lambda: os.environ.get("ADMIN_SECRET_KEY", "local-dev-only-change-me"))
    FRONTEND_URL: str = "http://localhost:5173"

    # Super admin (cuenta del fundador). Se siembra al arrancar si no existe.
    # IMPORTANTE: define SUPERADMIN_PASSWORD por entorno en producción.
    SUPERADMIN_EMAIL: str = "admin@agentepro.pe"
    SUPERADMIN_PASSWORD: str = Field(default_factory=lambda: os.environ.get("SUPERADMIN_PASSWORD", "local-dev-only-change-me"))
    SUPERADMIN_NAME: str = "Super Admin"

    # Permite registro self-service sin pago real (cobro simulado mientras no
    # haya CULQI_SECRET_KEY). En producción con Culqi real, exige token de pago.
    ALLOW_FREE_SIGNUP: bool = True

    # En producción (Railway) se define DATABASE_URL por entorno; en desarrollo se
    # arma a partir de POSTGRES_* (sin credenciales literales en el código).
    DATABASE_URL: str = Field(default_factory=_default_database_url)
    DATABASE_URL_SYNC: str = Field(default_factory=lambda: _default_database_url().replace("+asyncpg", "+psycopg2"))

    REDIS_URL: str = "redis://localhost:6379/0"

    # Permite desactivar el rate-limit (p. ej. en tests). En prod siempre True.
    RATE_LIMIT_ENABLED: bool = True

    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL_DEFAULT: str = "claude-sonnet-4-6"
    CLAUDE_MODEL_COMPLEX: str = "claude-opus-4-7"
    CLAUDE_MAX_TOKENS: int = 1024

    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_VERIFY_TOKEN_SECRET: str = "verify-token-secret"

    META_INSTAGRAM_APP_ID: str = ""
    META_INSTAGRAM_APP_SECRET: str = ""

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_DEFAULT_PHONE_NUMBER: str = ""
    # Número WhatsApp de Twilio para ENVIAR (sandbox por defecto). En producción,
    # el número WhatsApp aprobado del negocio. Formato E.164 sin "whatsapp:".
    TWILIO_WHATSAPP_FROM: str = "+14155238886"

    # Citas: cuántas horas antes se manda el recordatorio automático al cliente.
    REMINDER_WINDOW_HOURS: int = 24

    RETELL_API_KEY: str = ""
    # ID de voz de Retell (su catálogo propio, NO nombres de Azure/Neural).
    # Femenina en español latinoamericano. Otras: cartesia-Isabel, cartesia-Elena,
    # 11labs-Santiago (masc). Ver /list-voices de Retell para el catálogo completo.
    RETELL_DEFAULT_VOICE_ID: str = "cartesia-Hailey-Spanish-latin-america"
    RETELL_WEBHOOK_SECRET: str = ""
    # OJO: Retell usa NOMBRES DE MODELO PROPIOS (no los de la API de Anthropic).
    # Valores válidos hoy: claude-4.6-sonnet, claude-4.5-sonnet, claude-4.0-sonnet,
    # claude-4.5-haiku, gpt-4o, etc. NO acepta "claude-opus-4-8" ni "claude-sonnet-4-6".
    RETELL_LLM_MODEL: str = "claude-4.6-sonnet"

    HUBSPOT_ACCESS_TOKEN: str = ""
    HUBSPOT_PORTAL_ID: str = ""

    MODAL_TOKEN_ID: str = ""
    MODAL_TOKEN_SECRET: str = ""

    FAL_KEY: str = ""

    CULQI_PUBLIC_KEY: str = ""
    CULQI_SECRET_KEY: str = ""
    CULQI_WEBHOOK_SECRET: str = ""

    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@agentepro.pe"

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "agentepro-media"

    # Datos de cobro manual (sin pasarela). Se muestran al negocio en la pantalla de
    # pago/upgrade para que te pague por adelantado por Yape/transferencia.
    PAYMENT_YAPE_NUMBER: str = ""       # número de Yape/Plin (ej. 999 999 999)
    PAYMENT_ACCOUNT_HOLDER: str = ""    # titular de la cuenta / nombre del Yape
    PAYMENT_BANK_ACCOUNT: str = ""      # banco + número de cuenta / CCI
    PAYMENT_CONTACT_WHATSAPP: str = ""  # WhatsApp para enviar el comprobante (ej. 51999...)
    PAYMENT_NOTE: str = ""              # nota opcional (instrucciones extra)

    # Topes mensuales por plan (mensajes IA y llamadas de voz). Llamadas=0 => el
    # plan NO incluye voz. "Enterprise ilimitado" es en realidad un TOPE DE USO
    # JUSTO alto: con voz a ~S/1.5/llamada, un "ilimitado" real haría perder plata.
    PLAN_INICIAL_MESSAGES: int = 200
    PLAN_INICIAL_CALLS: int = 0
    PLAN_BASIC_MESSAGES: int = 400
    PLAN_BASIC_CALLS: int = 0
    PLAN_PROFESSIONAL_MESSAGES: int = 1500
    PLAN_PROFESSIONAL_CALLS: int = 60
    PLAN_ENTERPRISE_MESSAGES: int = 4000
    PLAN_ENTERPRISE_CALLS: int = 150
    # Trial (14 días): funciones de Profesional pero topes de prueba muy bajos,
    # para que el riesgo máximo por prueba sea ~S/25. Se cuenta desde el día 1.
    PLAN_TRIAL_MESSAGES: int = 200
    PLAN_TRIAL_CALLS: int = 10

    # Precios de venta (S/) y costo estimado de APIs por plan (S/), de PRICING.md.
    # Usados por el panel de Super Admin para calcular ingresos y ganancia.
    PLAN_INICIAL_PRICE: float = 149.0
    PLAN_BASIC_PRICE: float = 249.0
    PLAN_PROFESSIONAL_PRICE: float = 449.0
    PLAN_ENTERPRISE_PRICE: float = 799.0
    PLAN_INICIAL_COST_EST: float = 14.0
    PLAN_BASIC_COST_EST: float = 24.0
    PLAN_PROFESSIONAL_COST_EST: float = 173.0
    PLAN_ENTERPRISE_COST_EST: float = 435.0
    USD_TO_PEN: float = 3.75
    CLAUDE_USD_PER_MTOK: float = 5.0
    # Costo REAL por unidad consumida (para calcular el costo verdadero por negocio,
    # no estimado). Las CANTIDADES son reales (tokens, segundos de llamada,
    # conversaciones); estas tarifas las ajustas para que cuadren con tus facturas.
    RETELL_USD_PER_MIN: float = 0.07  # voz IA (Retell), por minuto
    TWILIO_USD_PER_MIN: float = 0.014  # telefonía (Twilio), por minuto
    WHATSAPP_USD_PER_CONVERSATION: float = 0.005  # Meta: conversaciones de servicio (ajustable)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _normalize_database_urls(self) -> "Settings":
        """Acepta la DATABASE_URL "cruda" que dan hosts como Railway/Heroku
        (`postgres://...` o `postgresql://...`, sin driver) y la adapta a las que
        usa la app: asíncrona (asyncpg) para el motor y síncrona (psycopg2) para
        Alembic. Así en Railway basta con definir DATABASE_URL y todo funciona.
        No toca URLs de SQLite (tests) ni las que ya traen driver explícito.
        """
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://") :]
        self.DATABASE_URL = url
        if url.startswith("postgresql+asyncpg://"):
            # La URL síncrona (Alembic) se deriva de la async: mismo destino.
            self.DATABASE_URL_SYNC = url.replace("+asyncpg", "+psycopg2")
        return self


settings = Settings()
