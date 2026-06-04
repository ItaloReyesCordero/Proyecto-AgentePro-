Eres el arquitecto principal de **AgentePro 2.0** — una plataforma SaaS multi-tenant de automatización de negocios con inteligencia artificial para el mercado peruano y latinoamericano. Vas a construir el sistema completo, end-to-end, production-ready, desde cero, en esta carpeta. No pares hasta construir TODO lo que se describe aquí.

---

## VISIÓN DEL PRODUCTO

AgentePro 2.0 es la plataforma más completa de automatización para negocios pequeños y medianos en Perú. Cada negocio que paga recibe automáticamente:

- **Agente WhatsApp IA** — responde 24/7, califica leads, agenda citas
- **Agente de Voz IA** — contesta y hace llamadas en español natural
- **CRM automático con HubSpot** — registra todo sin que nadie haga nada
- **Automatizaciones con Modal** — follow-ups, reportes, tareas programadas
- **Generador de contenido Instagram** — posts con imagen y texto generados por IA
- **Dashboard unificado** — el dueño ve todo en un solo lugar
- **Auto-provisioning** — al pagar, todo se configura solo en segundos

---

## STACK TECNOLÓGICO — VERSIONES EXACTAS

### Backend
- Python 3.13 con `uv` como gestor (NO pip directo)
- FastAPI 0.115+ con lifespan events
- SQLAlchemy 2.0+ async con asyncpg
- Alembic para migraciones
- Pydantic v2 para validación
- anthropic SDK 0.40+ (claude-sonnet-4-6 por defecto, claude-opus-4-8 para tareas complejas)
- retell-ai SDK (agente de voz)
- twilio SDK (números telefónicos)
- hubspot-api-client (CRM)
- modal SDK (automatizaciones en la nube)
- httpx para requests async
- python-jose para JWT
- passlib[bcrypt] para passwords
- redis para caché y rate limiting
- celery con redis broker
- structlog para logging estructurado
- cryptography (Fernet) para encriptar tokens de terceros
- python-socketio para tiempo real
- resend para emails transaccionales
- pytest + pytest-asyncio para tests

### Frontend
- React 19 con Vite 6
- TypeScript 5.7+ estricto (nunca `any`)
- Tailwind CSS v4
- React Router v7
- TanStack Query v5
- TanStack Table v8
- Recharts 2.x
- Zustand para estado global
- React Hook Form + Zod
- shadcn/ui
- Lucide React
- date-fns
- socket.io-client
- react-player (para reproducir grabaciones de llamadas)

### Servicios externos
- **Meta WhatsApp Business API** — mensajes WhatsApp
- **Meta Graph API** — Instagram DMs y publicaciones
- **Twilio** — números telefónicos
- **Retell AI** — agente de voz en español
- **HubSpot API Free** — CRM con pipeline de ventas
- **Modal** — automatizaciones serverless
- **fal.ai** — generación de imágenes para Instagram
- **Supabase** — PostgreSQL + Storage
- **Railway** — deploy del backend
- **Vercel** — deploy del frontend
- **Culqi** — pagos con tarjeta y Yape (Perú)
- **Resend** — emails transaccionales

---

## ESTRUCTURA COMPLETA DE CARPETAS

Crea exactamente esta estructura:

```
agentepro/
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env.example
│   ├── Dockerfile
│   ├── railway.json
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_calls_instagram_hubspot.py
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── tenant.py
│       │   ├── user.py
│       │   ├── conversation.py
│       │   ├── message.py
│       │   ├── contact.py
│       │   ├── agent_config.py
│       │   ├── voice_config.py
│       │   ├── call.py
│       │   ├── call_summary.py
│       │   ├── instagram_post.py
│       │   ├── automation.py
│       │   ├── automation_run.py
│       │   ├── subscription.py
│       │   ├── hubspot_sync_log.py
│       │   └── webhook_log.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── tenant.py
│       │   ├── user.py
│       │   ├── auth.py
│       │   ├── conversation.py
│       │   ├── message.py
│       │   ├── contact.py
│       │   ├── agent_config.py
│       │   ├── voice_config.py
│       │   ├── call.py
│       │   ├── instagram.py
│       │   ├── automation.py
│       │   ├── metrics.py
│       │   ├── webhook_meta.py
│       │   └── webhook_retell.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py
│       │       ├── auth.py
│       │       ├── tenants.py
│       │       ├── conversations.py
│       │       ├── messages.py
│       │       ├── contacts.py
│       │       ├── agent.py
│       │       ├── voice.py
│       │       ├── calls.py
│       │       ├── instagram.py
│       │       ├── automations.py
│       │       ├── metrics.py
│       │       ├── subscriptions.py
│       │       ├── provisioning.py
│       │       └── admin.py
│       ├── webhooks/
│       │   ├── __init__.py
│       │   ├── meta_whatsapp.py
│       │   ├── meta_instagram.py
│       │   ├── retell.py
│       │   ├── twilio_voice.py
│       │   └── culqi.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── security.py
│       │   ├── exceptions.py
│       │   ├── middleware.py
│       │   └── socket.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── whatsapp/
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── webhook_handler.py
│       │   │   ├── message_parser.py
│       │   │   └── sender.py
│       │   ├── instagram/
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── post_generator.py
│       │   │   ├── dm_handler.py
│       │   │   └── scheduler.py
│       │   ├── voice/
│       │   │   ├── __init__.py
│       │   │   ├── retell_client.py
│       │   │   ├── twilio_client.py
│       │   │   ├── call_handler.py
│       │   │   └── outbound_caller.py
│       │   ├── ai/
│       │   │   ├── __init__.py
│       │   │   ├── agent.py
│       │   │   ├── voice_agent.py
│       │   │   ├── prompt_builder.py
│       │   │   ├── voice_prompt_builder.py
│       │   │   ├── context_manager.py
│       │   │   ├── intent_detector.py
│       │   │   ├── lead_scorer.py
│       │   │   ├── call_summarizer.py
│       │   │   ├── instagram_content_generator.py
│       │   │   └── response_formatter.py
│       │   ├── crm/
│       │   │   ├── __init__.py
│       │   │   ├── hubspot_client.py
│       │   │   ├── contact_sync.py
│       │   │   ├── deal_manager.py
│       │   │   └── pipeline_updater.py
│       │   ├── provisioning/
│       │   │   ├── __init__.py
│       │   │   ├── tenant_provisioner.py
│       │   │   ├── twilio_provisioner.py
│       │   │   ├── retell_provisioner.py
│       │   │   └── hubspot_provisioner.py
│       │   ├── conversation_service.py
│       │   ├── contact_service.py
│       │   ├── call_service.py
│       │   ├── metrics_service.py
│       │   ├── notification_service.py
│       │   └── culqi_service.py
│       ├── modal_tasks/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── follow_up_leads.py
│       │   ├── instagram_scheduler.py
│       │   ├── weekly_reports.py
│       │   ├── audio_transcriber.py
│       │   └── bulk_campaigns.py
│       ├── workers/
│       │   ├── __init__.py
│       │   ├── celery_app.py
│       │   ├── email_tasks.py
│       │   └── reminder_tasks.py
│       └── utils/
│           ├── __init__.py
│           ├── logger.py
│           ├── encryption.py
│           └── helpers.py
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── .env.example
│   ├── vercel.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── router.tsx
│       ├── types/
│       │   ├── index.ts
│       │   ├── conversation.ts
│       │   ├── call.ts
│       │   ├── contact.ts
│       │   ├── instagram.ts
│       │   ├── automation.ts
│       │   └── metrics.ts
│       ├── lib/
│       │   ├── api.ts
│       │   ├── auth.ts
│       │   ├── socket.ts
│       │   └── utils.ts
│       ├── stores/
│       │   ├── auth.store.ts
│       │   └── ui.store.ts
│       ├── hooks/
│       │   ├── useConversations.ts
│       │   ├── useMessages.ts
│       │   ├── useCalls.ts
│       │   ├── useContacts.ts
│       │   ├── useInstagram.ts
│       │   ├── useAutomations.ts
│       │   ├── useMetrics.ts
│       │   └── useSocket.ts
│       ├── components/
│       │   ├── ui/
│       │   ├── layout/
│       │   │   ├── AppLayout.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── TopBar.tsx
│       │   ├── conversations/
│       │   │   ├── ConversationList.tsx
│       │   │   ├── ConversationItem.tsx
│       │   │   ├── MessageThread.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   └── TakeControlButton.tsx
│       │   ├── calls/
│       │   │   ├── CallList.tsx
│       │   │   ├── CallItem.tsx
│       │   │   ├── CallTranscript.tsx
│       │   │   ├── CallSummary.tsx
│       │   │   └── OutboundCallButton.tsx
│       │   ├── contacts/
│       │   │   ├── ContactList.tsx
│       │   │   ├── ContactCard.tsx
│       │   │   ├── LeadScoreBadge.tsx
│       │   │   └── PipelineView.tsx
│       │   ├── instagram/
│       │   │   ├── PostCalendar.tsx
│       │   │   ├── PostCard.tsx
│       │   │   ├── PostGenerator.tsx
│       │   │   └── PostPreview.tsx
│       │   ├── automations/
│       │   │   ├── AutomationList.tsx
│       │   │   ├── AutomationCard.tsx
│       │   │   └── AutomationToggle.tsx
│       │   ├── metrics/
│       │   │   ├── MetricsGrid.tsx
│       │   │   ├── MessageVolumeChart.tsx
│       │   │   ├── LeadFunnelChart.tsx
│       │   │   ├── CallsChart.tsx
│       │   │   └── RevenueCard.tsx
│       │   ├── agent/
│       │   │   ├── AgentConfigForm.tsx
│       │   │   ├── VoiceConfigForm.tsx
│       │   │   ├── FAQEditor.tsx
│       │   │   └── PersonalitySelector.tsx
│       │   └── common/
│       │       ├── StatusBadge.tsx
│       │       ├── PhonePreview.tsx
│       │       ├── AudioPlayer.tsx
│       │       └── EmptyState.tsx
│       └── pages/
│           ├── auth/
│           │   ├── LoginPage.tsx
│           │   └── RegisterPage.tsx
│           ├── dashboard/
│           │   └── DashboardPage.tsx
│           ├── conversations/
│           │   └── ConversationsPage.tsx
│           ├── calls/
│           │   └── CallsPage.tsx
│           ├── contacts/
│           │   └── ContactsPage.tsx
│           ├── instagram/
│           │   └── InstagramPage.tsx
│           ├── automations/
│           │   └── AutomationsPage.tsx
│           ├── agent/
│           │   └── AgentConfigPage.tsx
│           ├── settings/
│           │   └── SettingsPage.tsx
│           └── onboarding/
│               └── OnboardingPage.tsx
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .gitignore
└── README.md
```

---

## FASE 1 — FUNDACIÓN Y BASE DE DATOS

### 1.1 Inicializa el proyecto backend

```bash
uv init backend --python 3.13
cd backend

uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg alembic \
    pydantic "pydantic-settings" anthropic httpx "python-jose[cryptography]" \
    "passlib[bcrypt]" python-multipart redis celery structlog \
    python-dotenv email-validator phonenumbers cryptography \
    python-socketio retell-ai twilio hubspot-api-client \
    modal resend fal-client

uv add --dev pytest pytest-asyncio httpx pytest-cov ruff mypy
```

### 1.2 Inicializa el frontend

```bash
cd ../
npm create vite@latest frontend -- --template react-ts
cd frontend

npm install @tanstack/react-query@5 @tanstack/react-table@8 \
    react-router-dom@7 recharts zustand react-hook-form \
    @hookform/resolvers zod axios socket.io-client date-fns \
    lucide-react class-variance-authority clsx tailwind-merge \
    react-player @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
    @radix-ui/react-tabs @radix-ui/react-toast

npm install -D tailwindcss@4 @vitejs/plugin-react typescript@5.7 \
    @types/node autoprefixer
```

### 1.3 Crea el pyproject.toml completo

Incluye:
- Configuración de ruff (linting + formatting)
- Configuración de mypy estricto
- pytest con asyncio_mode = "auto"
- Scripts: `dev` (uvicorn con hot reload), `test`, `migrate`, `worker`, `modal-deploy`

### 1.4 Crea todos los modelos SQLAlchemy 2.0

**`app/models/tenant.py`**
```python
# Campos:
# id: UUID primary key
# name: str — nombre del negocio
# slug: str — unique, para URLs y webhooks
# business_type: Enum('clinica','academia','tienda','seguros','restaurante','otro')
# phone_number_id: str — ID del número en Meta (WhatsApp)
# waba_id: str — WhatsApp Business Account ID
# whatsapp_access_token: str — encriptado con Fernet
# webhook_verify_token: str — único por tenant
# twilio_phone_number: str — número Twilio asignado
# retell_agent_id: str — ID del agente de voz en Retell
# hubspot_company_id: str — ID de la empresa en HubSpot
# instagram_account_id: str — ID de cuenta de Instagram
# instagram_access_token: str — encriptado
# plan: Enum('basic','professional','enterprise')
# messages_used_this_month: int default 0
# calls_used_this_month: int default 0
# is_active: bool default True
# is_provisioned: bool default False — True cuando auto-provisioning completó
# trial_ends_at: datetime
# created_at, updated_at: datetime
# Relaciones: users, conversations, contacts, agent_config, voice_config,
#             calls, instagram_posts, automations, subscription
```

**`app/models/agent_config.py`**
```python
# Campos:
# id: UUID
# tenant_id: UUID FK
# business_name: str
# agent_name: str — nombre del asistente (ej: "María")
# personality: Enum('formal','amigable','profesional','energico')
# language: str default 'es-PE'
# greeting_message: str
# business_hours: JSON — {"lunes":{"open":"08:00","close":"18:00","active":true},...}
# outside_hours_message: str
# faqs: JSON — [{"question": str, "answer": str, "category": str}]
# services: JSON — [{"name": str, "description": str, "price": float, "currency": "PEN"}]
# escalation_phone: str
# escalation_keywords: JSON — ["urgente","emergencia","hablar con","quiero quejarme"]
# escalation_email: str
# appointment_enabled: bool default False
# appointment_duration_minutes: int default 30
# appointment_confirmation_message: str
# lead_qualification_questions: JSON — preguntas para calificar leads
# custom_instructions: str — texto libre con instrucciones adicionales
# is_active: bool default True
# updated_at: datetime
```

**`app/models/voice_config.py`**
```python
# Campos:
# id: UUID
# tenant_id: UUID FK
# agent_name: str — nombre que dice en la llamada ("Hola, soy María de...")
# voice_id: str — ID de la voz en Retell (española, natural)
# language: str default 'es-419' — español latinoamericano
# greeting_script: str — qué dice al contestar
# max_call_duration_seconds: int default 300
# allow_outbound_calls: bool default True
# outbound_calling_hours: JSON — horario permitido para llamadas salientes
# voicemail_message: str — si no contestan
# call_recording_enabled: bool default True
# transcription_enabled: bool default True
# is_active: bool default True
```

**`app/models/call.py`**
```python
# Campos:
# id: UUID
# tenant_id: UUID FK
# contact_id: UUID FK nullable
# retell_call_id: str — ID único de la llamada en Retell
# twilio_call_sid: str — SID de Twilio
# direction: Enum('inbound','outbound')
# from_number: str
# to_number: str
# status: Enum('initiated','ringing','in_progress','completed','failed','no_answer','voicemail')
# duration_seconds: int
# recording_url: str — URL de la grabación (en Supabase Storage)
# transcript: text — transcripción completa
# ai_summary: text — resumen generado por Claude
# intent_detected: str — qué quería el cliente
# outcome: Enum('appointment_booked','info_provided','escalated','follow_up_needed','sale','no_interest')
# lead_score_before: int
# lead_score_after: int
# tokens_used: int
# started_at: datetime
# ended_at: datetime
# created_at: datetime
```

**`app/models/call_summary.py`**
```python
# Campos:
# id: UUID
# call_id: UUID FK
# tenant_id: UUID FK
# key_points: JSON — lista de puntos clave de la llamada
# action_items: JSON — acciones a tomar después
# sentiment: Enum('positive','neutral','negative')
# follow_up_required: bool
# follow_up_date: datetime nullable
# follow_up_notes: str
# hubspot_synced: bool default False
# created_at: datetime
```

**`app/models/instagram_post.py`**
```python
# Campos:
# id: UUID
# tenant_id: UUID FK
# caption: text — texto del post generado por Claude
# image_url: str — URL de imagen generada por fal.ai (en Supabase Storage)
# image_prompt: str — el prompt usado para generar la imagen
# hashtags: JSON — lista de hashtags
# status: Enum('draft','pending_approval','approved','scheduled','published','failed')
# scheduled_for: datetime nullable
# published_at: datetime nullable
# instagram_post_id: str — ID del post publicado en Instagram
# instagram_permalink: str
# likes_count: int default 0
# comments_count: int default 0
# approved_by: UUID FK nullable — usuario que aprobó
# rejection_reason: str
# created_at, updated_at: datetime
```

**`app/models/automation.py`**
```python
# Campos:
# id: UUID
# tenant_id: UUID FK
# name: str
# type: Enum('lead_followup_whatsapp','lead_followup_call','appointment_reminder',
#             'weekly_report','birthday_message','post_visit_survey',
#             'inactive_contact_reactivation','bulk_campaign')
# is_active: bool default True
# trigger_config: JSON — condiciones que activan la automatización
#   ej: {"trigger": "no_response_hours", "value": 24, "lead_stage": "hot"}
# action_config: JSON — qué hacer
#   ej: {"action": "send_whatsapp", "message_template": "...", "max_attempts": 3}
# schedule_config: JSON — para automatizaciones programadas
#   ej: {"frequency": "weekly", "day": "monday", "time": "09:00"}
# total_runs: int default 0
# successful_runs: int default 0
# last_run_at: datetime
# created_at, updated_at: datetime
```

**`app/models/conversation.py`**
```python
# id: UUID
# tenant_id: UUID FK
# contact_id: UUID FK
# wa_conversation_id: str
# channel: Enum('whatsapp','instagram_dm') default 'whatsapp'
# status: Enum('open','human_takeover','closed','waiting','bot_paused')
# assigned_to_human: bool default False
# human_takeover_at: datetime nullable
# last_message_at: datetime
# lead_score: int 0-100
# lead_stage: Enum('cold','warm','hot','customer','lost')
# tags: JSON
# hubspot_contact_id: str nullable
# hubspot_deal_id: str nullable
# created_at, updated_at
```

**`app/models/contact.py`**
```python
# id: UUID
# tenant_id: UUID FK
# wa_id: str — número de WhatsApp
# phone: str
# name: str nullable
# email: str nullable
# profile_picture_url: str nullable
# city: str nullable
# source: Enum('whatsapp','instagram','call','manual')
# lead_score: int 0-100
# lead_stage: Enum('cold','warm','hot','customer','lost')
# total_interactions: int default 0
# last_interaction_at: datetime
# hubspot_contact_id: str nullable
# tags: JSON
# custom_fields: JSON
# notes: text nullable
# created_at, updated_at
```

Crea **ambas migraciones Alembic** (001 para las tablas principales, 002 para las nuevas de llamadas e Instagram).

---

## FASE 2 — CONFIGURACIÓN Y SEGURIDAD

### `app/config.py` — Settings completo con pydantic-settings

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "AgentePro"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ADMIN_SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Database
    DATABASE_URL: str  # postgresql+asyncpg://...
    DATABASE_URL_SYNC: str  # postgresql://... (para alembic)
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Anthropic
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL_DEFAULT: str = "claude-sonnet-4-6"
    CLAUDE_MODEL_COMPLEX: str = "claude-opus-4-8"
    CLAUDE_MAX_TOKENS: int = 1024
    
    # Meta WhatsApp
    META_APP_ID: str
    META_APP_SECRET: str
    META_VERIFY_TOKEN_SECRET: str  # para generar tokens únicos por tenant
    
    # Meta Instagram
    META_INSTAGRAM_APP_ID: str
    META_INSTAGRAM_APP_SECRET: str
    
    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_DEFAULT_PHONE_NUMBER: str
    
    # Retell AI
    RETELL_API_KEY: str
    RETELL_DEFAULT_VOICE_ID: str = "es-ES-ElviraNeural"  # voz española natural
    RETELL_WEBHOOK_SECRET: str
    
    # HubSpot
    HUBSPOT_ACCESS_TOKEN: str
    HUBSPOT_PORTAL_ID: str
    
    # Modal
    MODAL_TOKEN_ID: str
    MODAL_TOKEN_SECRET: str
    
    # fal.ai
    FAL_KEY: str
    
    # Culqi
    CULQI_PUBLIC_KEY: str
    CULQI_SECRET_KEY: str
    CULQI_WEBHOOK_SECRET: str
    
    # Resend
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "noreply@agentepro.pe"
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "agentepro-media"
    
    # Plans
    PLAN_BASIC_MESSAGES: int = 500
    PLAN_BASIC_CALLS: int = 30
    PLAN_PROFESSIONAL_MESSAGES: int = 2000
    PLAN_PROFESSIONAL_CALLS: int = 100
    PLAN_ENTERPRISE_MESSAGES: int = 999999
    PLAN_ENTERPRISE_CALLS: int = 999999
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

### `utils/encryption.py`
```python
# Usa Fernet (cryptography library) para encriptar/desencriptar:
# - access_tokens de WhatsApp
# - access_tokens de Instagram  
# - credentials de terceros
# La clave de encriptación se deriva del SECRET_KEY de la app
# Funciones: encrypt(text: str) -> str, decrypt(text: str) -> str
```

---

## FASE 3 — MOTOR IA PRINCIPAL

### `app/services/ai/prompt_builder.py`

Genera el system prompt dinámico para el agente de WhatsApp de cada negocio:

```python
def build_whatsapp_system_prompt(
    agent_config: AgentConfig,
    current_datetime: datetime,
    channel: str = "whatsapp"
) -> str:
    """
    El prompt más completo posible. Secciones:
    
    ## IDENTIDAD Y ROL
    Nombre del agente, nombre del negocio, tipo de negocio, personalidad exacta.
    Instrucción de tono según personalidad:
    - formal → "usted", lenguaje profesional, sin emojis excesivos
    - amigable → "tú", emojis moderados, tono cálido
    - profesional → balance entre formal y cercano
    - energico → exclamaciones, emojis, muy dinámico
    
    ## FUNCIONES PRINCIPALES
    1. Responder preguntas frecuentes con la información exacta del negocio
    2. Presentar servicios y precios cuando pregunten
    3. Calificar leads (detectar intención de compra, urgencia, presupuesto)
    4. Agendar citas si está habilitado
    5. Hacer seguimiento de interés ("¿Cuándo podrías venir?")
    6. Escalar a humano cuando sea necesario
    
    ## HORARIO ACTUAL
    Hora actual en Perú: [datetime formateado]
    Horario del negocio: [desglose por día]
    ¿Está dentro del horario ahora? [Sí/No con lógica calculada]
    Si está fuera de horario: [mensaje personalizado]
    
    ## CATÁLOGO DE SERVICIOS
    [Lista formateada de servicios con precios en soles]
    
    ## BASE DE CONOCIMIENTO — PREGUNTAS FRECUENTES
    [Lista de FAQs con sus respuestas exactas, agrupadas por categoría]
    
    ## SISTEMA DE CALIFICACIÓN DE LEADS
    Mientras conversas, evalúa y actualiza mentalmente:
    - Interés: ¿está activamente buscando? (0-33 frío, 34-66 tibio, 67-100 caliente)
    - Urgencia: ¿necesita el servicio pronto?
    - Presupuesto: ¿mencionó que puede pagar?
    - Autoridad: ¿es quien decide la compra?
    
    ## CUÁNDO ESCALAR A HUMANO
    Escala INMEDIATAMENTE si el cliente dice alguna de estas palabras: [lista]
    Escala también si:
    - Pregunta algo que no sabes y es crítico para su decisión
    - Expresa molestia o frustración clara
    - Lleva más de 5 mensajes sin resolverse
    - La consulta es técnica/legal/médica fuera de tu alcance
    
    Al escalar, di EXACTAMENTE: "[mensaje de escalado del negocio]"
    Y agrega al final de tu respuesta: <!--ACTION:ESCALATE-->
    
    ## METADATOS DE RESPUESTA (MUY IMPORTANTE)
    Al final de CADA respuesta, agrega este bloque oculto:
    <!--META:{"intent":"faq|appointment|lead|escalation|greeting|followup",
               "confidence":0.95,
               "lead_score":75,
               "lead_stage":"warm",
               "actions":["book_appointment","create_deal","notify_owner"],
               "appointment_date":null,
               "key_info_extracted":{"service_interest":"consulta","budget":null}}-->
    
    ## INSTRUCCIONES ESPECIALES DEL NEGOCIO
    [custom_instructions del negocio - texto libre]
    
    ## REGLAS ABSOLUTAS (nunca violar)
    1. Nunca inventes precios que no están en tu lista
    2. Nunca hagas promesas que el negocio no puede cumplir
    3. No digas que eres una IA a menos que insistan 3+ veces
    4. Respuestas máximo 3 párrafos — WhatsApp es conversación, no email
    5. Si mandan audio: "Hola 😊 Por ahora solo puedo leer texto. ¿Puedes escribirme?"
    6. Si mandan imagen: responde según el contexto (foto de producto → comenta sobre él)
    7. Usa el nombre del cliente si lo sabes
    8. Termina siempre con una pregunta para mantener la conversación viva
    """
```

### `app/services/ai/voice_prompt_builder.py`

System prompt específico para el agente de VOZ:

```python
def build_voice_system_prompt(
    voice_config: VoiceConfig,
    agent_config: AgentConfig,
    call_direction: str,  # 'inbound' | 'outbound'
    contact_context: dict = None  # datos del contacto si es llamada saliente
) -> str:
    """
    Secciones del prompt de voz:
    
    ## CONTEXTO DE LLAMADA
    Eres [nombre], asistente de voz de [negocio].
    Tipo de llamada: [entrante/saliente]
    Si es saliente: contexto del contacto (nombre, qué consultó antes, lead score)
    
    ## GUIÓN DE APERTURA
    Exactamente qué decir al contestar/marcar:
    Entrante: "Buenas [tardes/días], habla con [nombre] de [negocio]. ¿En qué le puedo ayudar?"
    Saliente: "Hola [nombre del contacto], le llamo de [negocio]. Le contactamos porque [razón]..."
    
    ## FLUJO DE CONVERSACIÓN DE VOZ
    Reglas especiales para voz (diferente a texto):
    - Habla de forma natural, con pausas
    - No uses listas ni bullet points
    - Confirma que te entendieron: "¿Le quedó claro?" / "¿Tiene alguna pregunta?"
    - Si no te entienden, reformula de forma diferente
    - Máximo 2-3 oraciones por turno de habla
    
    ## SERVICIOS Y PRECIOS (versión oral)
    Cómo mencionar los precios hablando (no en lista, sino naturalmente)
    
    ## MANEJO DE SITUACIONES COMUNES
    - Si piden hablar con una persona: "Por supuesto, le conecto. ¿Me permite su nombre?"
    - Si la línea tiene ruido: "Disculpe, ¿me puede repetir eso?"
    - Si quieren agendar: flujo de confirmación de fecha y hora
    - Si dicen que están ocupados: "Entiendo perfectamente, ¿cuándo sería un buen momento?"
    
    ## CIERRE DE LLAMADA
    Cómo terminar según el resultado:
    - Cita agendada: confirma fecha, hora, servicio y dice que recibirán WhatsApp con recordatorio
    - Sin interés: "Perfecto, si en algún momento lo necesita, aquí estamos. ¡Que tenga buen día!"
    - Escalada: "Le voy a conectar con [nombre] del equipo. Un momento por favor."
    
    ## METADATOS (al terminar la llamada, en el último mensaje)
    <!--CALL_META:{"outcome":"appointment_booked|info_provided|escalated|follow_up_needed|no_interest",
                   "appointment_date":null,
                   "follow_up_required":true,
                   "key_points":["interesado en servicio X","presupuesto Y"],
                   "action_items":["enviar cotización","llamar el viernes"]}-->
    """
```

### `app/services/ai/agent.py` — Motor principal WhatsApp

```python
class AIAgentService:
    
    async def process_whatsapp_message(
        self,
        message_content: str,
        message_type: str,  # text, audio, image, document
        conversation: Conversation,
        tenant: Tenant,
        agent_config: AgentConfig,
        db: AsyncSession
    ) -> AgentResponse:
        """
        Flujo completo:
        1. Verifica límite de mensajes del plan
        2. Si es audio → transcribe con Whisper antes de procesar
        3. Obtiene últimos 20 mensajes de contexto
        4. Construye system prompt dinámico
        5. Llama Claude API (streaming interno, no al cliente)
        6. Parsea el bloque <!--META:...--> de la respuesta
        7. Limpia la respuesta (elimina bloque META)
        8. Si detecta ESCALATE → marca conversación y notifica
        9. Actualiza lead_score y lead_stage en conversación y contacto
        10. Si detecta appointment → crea tarea en HubSpot
        11. Si lead_score > 70 → crea deal en HubSpot automáticamente
        12. Guarda mensaje outbound en DB
        13. Actualiza contador de mensajes del tenant
        14. Emite evento socket.io al dashboard
        15. Retorna AgentResponse
        """
    
    async def process_instagram_dm(
        self,
        message_content: str,
        conversation: Conversation,
        tenant: Tenant,
        agent_config: AgentConfig,
        db: AsyncSession
    ) -> AgentResponse:
        """Igual que WhatsApp pero con channel='instagram_dm'"""
```

### `app/services/ai/call_summarizer.py`

```python
async def summarize_call(
    transcript: str,
    call: Call,
    agent_config: AgentConfig,
    anthropic_client: AsyncAnthropic
) -> CallSummary:
    """
    Llama a Claude con el transcript completo.
    
    Prompt para Claude:
    "Analiza esta transcripción de llamada de negocios y extrae:
    1. Puntos clave de la conversación (máximo 5 bullets)
    2. Qué quería el cliente exactamente
    3. Cómo terminó la llamada
    4. Acciones pendientes o próximos pasos
    5. Sentimiento general del cliente (positivo/neutral/negativo)
    6. ¿Se requiere seguimiento? ¿Cuándo?
    
    Transcripción: [transcript]
    
    Responde SOLO en JSON con este formato exacto:
    {
      'key_points': [...],
      'client_intent': '...',
      'outcome': '...',
      'action_items': [...],
      'sentiment': 'positive|neutral|negative',
      'follow_up_required': true/false,
      'follow_up_suggested_date': 'YYYY-MM-DD o null',
      'follow_up_notes': '...'
    }"
    """
```

### `app/services/ai/instagram_content_generator.py`

```python
async def generate_post(
    tenant: Tenant,
    agent_config: AgentConfig,
    post_theme: str,  # 'service_highlight', 'promotion', 'tip', 'testimonial', 'seasonal'
    specific_service: str = None,
    anthropic_client: AsyncAnthropic = None
) -> InstagramPostDraft:
    """
    Paso 1 — Claude genera el caption y el prompt de imagen:
    
    System prompt a Claude:
    "Eres un experto en marketing digital para negocios peruanos.
    Negocio: [nombre], Tipo: [tipo], Personalidad de marca: [personalidad]
    Servicios: [lista]
    
    Genera un post de Instagram para el tema: [tema]
    Servicio específico (si aplica): [servicio]
    
    Responde SOLO en JSON:
    {
      'caption': 'texto del post en español peruano, máximo 150 palabras, 
                  con llamada a la acción clara, sin hashtags aquí',
      'hashtags': ['#hashtag1', '#hashtag2', ...], // máximo 15 hashtags relevantes
      'image_prompt': 'prompt en inglés detallado para generar imagen con fal.ai,
                       estilo profesional, colores que transmitan confianza,
                       relevante para el servicio/negocio, fotorrealista',
      'best_time_to_post': 'HH:MM',
      'post_type': 'feed|story|reel'
    }"
    
    Paso 2 — fal.ai genera la imagen:
    Usa fal_client.run("fal-ai/flux/schnell", arguments={"prompt": image_prompt})
    Descarga la imagen y súbela a Supabase Storage
    
    Retorna InstagramPostDraft con todo listo para aprobar
    """
```

---

## FASE 4 — WEBHOOKS

### `app/webhooks/meta_whatsapp.py`

```python
@router.get("/webhooks/whatsapp/{tenant_slug}")
async def verify_whatsapp_webhook(
    tenant_slug: str,
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
    db: AsyncSession = Depends(get_db)
):
    """
    Verificación Meta. CRÍTICO: retorna hub_challenge como texto plano puro,
    no como JSON. Status 200 exacto.
    Verifica tenant_slug + hub_verify_token contra DB.
    """

@router.post("/webhooks/whatsapp/{tenant_slug}")
async def receive_whatsapp_webhook(
    tenant_slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    SIEMPRE retorna 200 OK inmediatamente.
    Verifica firma HMAC-SHA256 con META_APP_SECRET.
    Procesa en background:
    
    Estructura del payload de Meta (muy anidada):
    entry[0].changes[0].value.messages[0] → mensaje
    entry[0].changes[0].value.statuses[0] → estado (delivered, read)
    
    Para mensajes:
    - Verifica wa_message_id no existe en DB (anti-duplicado)
    - Marca como leído inmediatamente (doble check azul)
    - Envía typing indicator (puntitos)
    - Busca/crea Contact por wa_id
    - Busca/crea Conversation
    - Si conversation.assigned_to_human == True → skip (humano está respondiendo)
    - Si conversation.status == 'bot_paused' → skip
    - Guarda mensaje inbound
    - Llama AIAgentService.process_whatsapp_message()
    - Envía respuesta via Meta API
    - Guarda mensaje outbound
    - Emite socket.io events
    - Sincroniza con HubSpot en background
    """
```

### `app/webhooks/retell.py`

```python
@router.post("/webhooks/retell/{tenant_slug}")
async def retell_webhook(
    tenant_slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe eventos de Retell AI para llamadas.
    
    Eventos a manejar:
    - call_started → crea registro Call en DB
    - call_ended → actualiza duración, status, guarda transcript
    - call_analyzed → transcript final disponible, lanza summarizer
    
    Para call_ended:
    1. Actualiza Call con duración y transcript
    2. En background: llama call_summarizer (Claude analiza transcript)
    3. Actualiza Contact con nueva información extraída
    4. Sincroniza con HubSpot (nota de actividad en el contacto)
    5. Si follow_up_required → crea tarea en HubSpot
    6. Si outcome == 'appointment_booked' → crea deal en HubSpot
    7. Emite socket.io event al dashboard
    """
```

### `app/webhooks/twilio_voice.py`

```python
@router.post("/webhooks/twilio/voice/{tenant_slug}")
async def twilio_incoming_call(
    tenant_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Twilio llama a este endpoint cuando llega una llamada al número del tenant.
    
    Responde con TwiML que redirige la llamada a Retell AI:
    
    <Response>
      <Connect>
        <Stream url="wss://api.retellai.com/audio-websocket/{retell_agent_id}">
          <Parameter name="tenant_id" value="{tenant_id}"/>
          <Parameter name="from_number" value="{from_number}"/>
        </Stream>
      </Connect>
    </Response>
    
    También crea el registro inicial de Call en DB.
    """
```

### `app/webhooks/meta_instagram.py`

```python
@router.get("/webhooks/instagram/{tenant_slug}")
async def verify_instagram_webhook(...):
    """Igual que WhatsApp pero para Instagram"""

@router.post("/webhooks/instagram/{tenant_slug}")
async def receive_instagram_webhook(...):
    """
    Recibe mensajes directos de Instagram.
    Procesa con AIAgentService.process_instagram_dm()
    Responde via Instagram Graph API
    """
```

---

## FASE 5 — SERVICIOS DE VOZ

### `app/services/voice/retell_client.py`

```python
class RetellClient:
    BASE_URL = "https://api.retellai.com"
    
    async def create_agent(
        self,
        agent_name: str,
        system_prompt: str,
        voice_id: str,
        language: str = "es-419"
    ) -> dict:
        """
        Crea un agente de voz en Retell AI.
        POST /create-agent
        Retorna el agent_id para guardar en el tenant.
        
        Configuración completa:
        - response_engine: {"type": "retell-llm", "llm_id": crear con create_retell_llm()}
        - voice_id: voz en español natural
        - language: "es-419" (español latinoamericano)
        - ambient_sound: "coffee-shop" o "office" según tipo de negocio
        - enable_backchannel: true (dice "ajá", "entiendo" mientras el cliente habla)
        - interruption_sensitivity: 0.8 (permite interrumpir naturalmente)
        - end_call_after_silence_ms: 15000
        """
    
    async def create_retell_llm(self, system_prompt: str) -> dict:
        """
        Crea el LLM de Retell que usa Claude como backend.
        POST /create-retell-llm
        model: "claude-opus-4-8"
        system_prompt: el prompt de voz del negocio
        """
    
    async def update_agent(self, agent_id: str, updates: dict) -> dict:
        """Actualiza el system prompt cuando el negocio cambia su config"""
    
    async def create_phone_call(
        self,
        agent_id: str,
        from_number: str,
        to_number: str,
        metadata: dict = None
    ) -> dict:
        """Inicia una llamada saliente via Retell"""
    
    async def get_call(self, call_id: str) -> dict:
        """Obtiene detalles y transcript de una llamada"""
```

### `app/services/voice/outbound_caller.py`

```python
class OutboundCallerService:
    
    async def call_lead(
        self,
        contact: Contact,
        tenant: Tenant,
        reason: str,  # 'follow_up', 'appointment_reminder', 'survey'
        db: AsyncSession
    ) -> Call:
        """
        Lanza llamada saliente a un lead.
        
        Verifica:
        1. ¿Está dentro del horario de llamadas del negocio?
        2. ¿El contacto no tiene flag 'do_not_call'?
        3. ¿No se le llamó en las últimas 4 horas?
        4. ¿El tenant no excedió límite de llamadas del plan?
        
        Si todo OK:
        1. Crea registro Call en DB con status 'initiated'
        2. Genera context para el agente (historial del contacto)
        3. Actualiza system prompt de Retell con el contexto
        4. Llama retell_client.create_phone_call()
        5. Retorna el Call creado
        """
```

---

## FASE 6 — CRM CON HUBSPOT

### `app/services/crm/hubspot_client.py`

```python
class HubSpotClient:
    
    async def create_or_update_contact(
        self,
        phone: str,
        name: str = None,
        email: str = None,
        properties: dict = None
    ) -> dict:
        """
        Busca contacto por teléfono. Si existe, actualiza. Si no, crea.
        Propiedades a sincronizar:
        - firstname, lastname
        - phone, email
        - lead_score (propiedad custom)
        - lead_stage → mapea a HubSpot lifecycle stages
        - source (whatsapp, instagram, llamada)
        - last_interaction_date
        - agentepro_tenant_id (propiedad custom)
        """
    
    async def create_deal(
        self,
        contact_id: str,
        deal_name: str,
        stage: str,
        amount: float = None,
        properties: dict = None
    ) -> dict:
        """Crea deal en el pipeline de ventas de HubSpot"""
    
    async def add_activity_note(
        self,
        contact_id: str,
        note: str,
        activity_type: str  # 'whatsapp_conversation', 'call', 'instagram_dm'
    ) -> dict:
        """Agrega nota de actividad al historial del contacto"""
    
    async def update_deal_stage(self, deal_id: str, new_stage: str) -> dict:
        """Actualiza etapa del deal en el pipeline"""
    
    async def create_task(
        self,
        contact_id: str,
        task_title: str,
        due_date: datetime,
        notes: str = None
    ) -> dict:
        """Crea tarea de seguimiento asignada al contacto"""
    
    async def setup_tenant_pipeline(self, company_name: str) -> dict:
        """
        Al crear un nuevo tenant, configura en HubSpot:
        1. Crea la empresa en HubSpot
        2. Configura propiedades custom si no existen
        Retorna hubspot_company_id
        """
```

---

## FASE 7 — AUTO-PROVISIONING

### `app/services/provisioning/tenant_provisioner.py`

```python
class TenantProvisioner:
    
    async def provision_new_tenant(
        self,
        tenant_data: TenantCreateSchema,
        db: AsyncSession
    ) -> Tenant:
        """
        El proceso más importante del sistema.
        Se ejecuta cuando un nuevo cliente paga.
        
        Ejecuta TODO en una transacción con rollback completo si algo falla:
        
        Paso 1 — Crea el Tenant en DB
        Paso 2 — Genera webhook_verify_token único
        Paso 3 — Crea AgentConfig con defaults inteligentes según business_type:
            - clinica: FAQs de citas, horarios, especialidades
            - academia: FAQs de matrícula, precios, modalidades
            - tienda: FAQs de productos, delivery, pagos
            - seguros: FAQs de pólizas, cotizaciones, coberturas
        
        Paso 4 — Compra número Twilio via API:
            client.available_phone_numbers('PE').local.list(area_code='51')
            Si no hay números peruanos, usa número USA
            Asigna el número al tenant
        
        Paso 5 — Configura número Twilio:
            Apunta el webhook de voz entrante a: 
            /webhooks/twilio/voice/{tenant_slug}
        
        Paso 6 — Crea LLM en Retell:
            system_prompt = build_voice_system_prompt(voice_config, agent_config, 'inbound')
            retell_llm = await retell_client.create_retell_llm(system_prompt)
        
        Paso 7 — Crea agente de voz en Retell:
            agent = await retell_client.create_agent(
                agent_name=agent_config.agent_name,
                llm_id=retell_llm['llm_id'],
                voice_id=voice_config.voice_id
            )
            Guarda retell_agent_id en tenant
        
        Paso 8 — Configura HubSpot:
            company = await hubspot_client.setup_tenant_pipeline(tenant_data.name)
            Guarda hubspot_company_id en tenant
        
        Paso 9 — Crea automatizaciones por defecto según plan:
            - Todos los planes: lead_followup_whatsapp (24h sin respuesta)
            - Professional+: lead_followup_call (48h sin respuesta)
            - Professional+: weekly_report
            - Enterprise: appointment_reminder, inactive_contact_reactivation
        
        Paso 10 — Marca tenant.is_provisioned = True
        
        Paso 11 — Envía email de bienvenida con:
            - Sus credenciales de acceso al dashboard
            - Su URL única de webhook para Meta: /webhooks/whatsapp/{slug}
            - Instrucciones paso a paso para conectar WhatsApp Business
            - Número de teléfono asignado
            - Link de onboarding interactivo
        
        Paso 12 — Emite evento para notificar al admin (tú como founder)
        
        Si CUALQUIER paso falla:
            - Rollback de DB
            - Libera número Twilio si fue comprado
            - Elimina agente Retell si fue creado
            - Loguea el error completo
            - Notifica al admin por email
            - Lanza excepción para que el endpoint retorne 500
        """
```

---

## FASE 8 — MODAL AUTOMATIZACIONES

### `app/modal_tasks/app.py`

```python
import modal

app = modal.App("agentepro-tasks")

# Imagen con todas las dependencias
image = modal.Image.debian_slim(python_version="3.13").pip_install(
    "anthropic", "httpx", "sqlalchemy[asyncio]", "asyncpg",
    "retell-ai", "twilio", "hubspot-api-client", "resend"
)
```

### `app/modal_tasks/follow_up_leads.py`

```python
@app.function(
    image=image,
    schedule=modal.Cron("0 9 * * *"),  # Corre todos los días a las 9 AM hora Perú
    secrets=[modal.Secret.from_name("agentepro-secrets")]
)
async def follow_up_leads():
    """
    Proceso diario de seguimiento automático:
    
    1. Busca en DB todos los tenants activos con automatización 'lead_followup_whatsapp' activa
    
    2. Para cada tenant, busca contactos que:
       - lead_stage IN ('warm', 'hot')
       - last_interaction_at < hace 24 horas (configurable)
       - No tienen follow_up_sent_at en las últimas 48 horas
       - No tienen flag do_not_contact
    
    3. Para cada contacto encontrado:
       a. Genera mensaje de seguimiento personalizado con Claude:
          "Basado en el historial de conversación de [nombre] con [negocio],
           genera un mensaje de seguimiento natural y no invasivo.
           No repitas exactamente lo que se dijo antes.
           Tono: [personalidad del negocio]
           Historial resumido: [últimos 3 mensajes]"
       b. Envía el mensaje via WhatsApp Meta API
       c. Actualiza follow_up_sent_at en el contacto
       d. Registra la automatización en automation_runs
    
    4. Para contactos con lead_followup_call activa y sin respuesta en 48h:
       a. Verifica horario de llamadas
       b. Llama a OutboundCallerService.call_lead()
    
    5. Envía reporte al admin de cuántos seguimientos se hicieron
    """

@app.function(image=image, secrets=[modal.Secret.from_name("agentepro-secrets")])
async def trigger_followup_for_contact(contact_id: str, tenant_id: str, reason: str):
    """Versión para trigger manual desde el dashboard o API"""
```

### `app/modal_tasks/instagram_scheduler.py`

```python
@app.function(
    image=image,
    schedule=modal.Cron("0 8 * * 1"),  # Lunes 8 AM — genera posts de la semana
    secrets=[modal.Secret.from_name("agentepro-secrets")]
)
async def generate_weekly_instagram_posts():
    """
    Para cada tenant con plan Professional o Enterprise y Instagram conectado:
    
    1. Determina los temas de posts de la semana según:
       - Servicios del negocio
       - Temporada del año
       - Posts previos (evita repetirse)
    
    2. Para cada post (genera 3 por semana):
       a. Llama instagram_content_generator.generate_post()
       b. Claude genera caption + hashtags + image_prompt
       c. fal.ai genera la imagen (flux/schnell model)
       d. Descarga imagen y sube a Supabase Storage
       e. Guarda InstagramPost con status='pending_approval'
       f. Programa para: martes, jueves, sábado a las 12pm
    
    3. Notifica al dueño por WhatsApp:
       "Hola! Generamos 3 posts para esta semana. 
        Entra al dashboard para revisarlos y aprobarlos 👉 [link]"

@app.function(image=image, secrets=[modal.Secret.from_name("agentepro-secrets")])
async def publish_scheduled_posts():
    """
    Corre cada hora: busca posts con status='scheduled' 
    cuyo scheduled_for <= ahora y los publica via Instagram Graph API.
    Actualiza status a 'published' con instagram_post_id.
    """
```

### `app/modal_tasks/weekly_reports.py`

```python
@app.function(
    image=image,
    schedule=modal.Cron("0 8 * * 1"),  # Lunes 8 AM
    secrets=[modal.Secret.from_name("agentepro-secrets")]
)
async def send_weekly_reports():
    """
    Para cada tenant activo, genera y envía reporte semanal por WhatsApp:
    
    Claude genera el reporte con este contexto:
    - Total mensajes recibidos esta semana vs semana anterior
    - Nuevos leads generados (cold/warm/hot)
    - Citas agendadas
    - Llamadas recibidas y realizadas
    - Posts de Instagram publicados y engagement
    - Top 3 preguntas más frecuentes
    - Contactos que necesitan seguimiento urgente
    
    Formato del mensaje de WhatsApp (conciso, máximo 20 líneas):
    "📊 *Reporte semanal de [nombre negocio]*
     Semana del [fecha] al [fecha]
     
     💬 WhatsApp: X mensajes | Y leads nuevos
     📞 Llamadas: X recibidas | Y realizadas  
     📸 Instagram: X posts | Y nuevos seguidores
     
     🔥 Leads calientes esta semana: [nombres]
     ⚡ Acción recomendada: [recomendación de Claude]
     
     Ver reporte completo: [link dashboard]"
    """
```

### `app/modal_tasks/audio_transcriber.py`

```python
@app.function(
    image=image.pip_install("openai"),  # para Whisper
    secrets=[modal.Secret.from_name("agentepro-secrets")]
)
async def transcribe_whatsapp_audio(audio_url: str, message_id: str, tenant_id: str):
    """
    Descarga el audio de WhatsApp (formato ogg/opus).
    Convierte a mp3 con ffmpeg.
    Transcribe con OpenAI Whisper API (más preciso que local).
    Actualiza el Message en DB con la transcripción.
    Retorna el texto para que el agente pueda responder.
    """
```

---

## FASE 9 — API REST COMPLETA

### `app/api/v1/provisioning.py`

```python
POST /api/v1/provision
"""
El endpoint más importante del sistema.
Body: {business_name, business_type, owner_name, owner_email, 
       owner_phone, plan, culqi_token}

Flujo:
1. Valida y procesa pago con Culqi
2. Si pago OK → llama TenantProvisioner.provision_new_tenant()
3. Retorna: {tenant_id, dashboard_url, webhook_url, phone_number, access_token}

Solo accesible con payment_token válido o admin key.
"""
```

### `app/api/v1/auth.py`
```
POST /api/v1/auth/register    → Registro (para onboarding manual en dev)
POST /api/v1/auth/login       → Login → access_token + refresh_token
POST /api/v1/auth/refresh     → Refresca token
POST /api/v1/auth/logout      → Invalida refresh token  
GET  /api/v1/auth/me          → Datos del usuario autenticado
```

### `app/api/v1/conversations.py`
```
GET    /api/v1/conversations                     → Lista paginada (filtros: status, channel, lead_stage, date)
GET    /api/v1/conversations/{id}                → Detalle
GET    /api/v1/conversations/{id}/messages       → Mensajes paginados
POST   /api/v1/conversations/{id}/takeover       → Tomar control humano
POST   /api/v1/conversations/{id}/release        → Devolver a IA
POST   /api/v1/conversations/{id}/messages       → Enviar mensaje manual
PATCH  /api/v1/conversations/{id}               → Actualizar tags, lead_stage
POST   /api/v1/conversations/{id}/pause-bot     → Pausar bot temporalmente
```

### `app/api/v1/calls.py`
```
GET    /api/v1/calls                     → Lista de llamadas (filtros: direction, outcome, date)
GET    /api/v1/calls/{id}                → Detalle + transcript + resumen
GET    /api/v1/calls/{id}/recording     → URL de grabación (signed URL de Supabase)
POST   /api/v1/calls/outbound           → Iniciar llamada saliente manual
GET    /api/v1/calls/{id}/summary       → Resumen generado por Claude
```

### `app/api/v1/instagram.py`
```
GET    /api/v1/instagram/posts           → Lista de posts (todos los estados)
POST   /api/v1/instagram/posts/generate → Genera nuevo post con IA
GET    /api/v1/instagram/posts/{id}     → Detalle del post
POST   /api/v1/instagram/posts/{id}/approve   → Aprueba y programa
POST   /api/v1/instagram/posts/{id}/reject    → Rechaza con motivo
POST   /api/v1/instagram/posts/{id}/publish   → Publica inmediatamente
DELETE /api/v1/instagram/posts/{id}     → Elimina borrador
GET    /api/v1/instagram/connect-url    → URL OAuth para conectar cuenta Instagram
POST   /api/v1/instagram/connect        → Guarda tokens de Instagram
```

### `app/api/v1/automations.py`
```
GET    /api/v1/automations              → Lista de automatizaciones del tenant
PATCH  /api/v1/automations/{id}        → Activar/desactivar/configurar
GET    /api/v1/automations/{id}/runs   → Historial de ejecuciones
POST   /api/v1/automations/{id}/run    → Ejecutar manualmente (llama Modal)
```

### `app/api/v1/agent.py`
```
GET    /api/v1/agent/config             → Config actual
PUT    /api/v1/agent/config             → Actualizar config completa
PATCH  /api/v1/agent/config            → Actualizar campos específicos
POST   /api/v1/agent/config/test       → Probar agente con mensaje de prueba
GET    /api/v1/agent/config/preview    → Ver el system prompt generado
PUT    /api/v1/agent/voice             → Actualizar config de voz
POST   /api/v1/agent/voice/test-call   → Llamada de prueba al número del tenant
```

### `app/api/v1/metrics.py`
```
GET /api/v1/metrics/summary            → KPIs del período (mensajes, leads, llamadas, posts)
GET /api/v1/metrics/messages-volume    → Volumen por día/semana/mes
GET /api/v1/metrics/leads-funnel       → Funnel de leads por etapa
GET /api/v1/metrics/calls              → Métricas de llamadas (duración, outcomes)
GET /api/v1/metrics/instagram          → Engagement de posts
GET /api/v1/metrics/response-time      → Tiempo promedio de respuesta
GET /api/v1/metrics/costs              → Costo estimado Claude API + Twilio + Retell
GET /api/v1/metrics/top-questions      → FAQs más consultadas
```

### `app/api/v1/contacts.py`
```
GET    /api/v1/contacts                 → Lista con filtros (lead_stage, source, date)
GET    /api/v1/contacts/{id}            → Detalle con historial completo
PATCH  /api/v1/contacts/{id}           → Actualizar datos, notas, tags
GET    /api/v1/contacts/{id}/conversations → Todas las conversaciones del contacto
GET    /api/v1/contacts/{id}/calls     → Todas las llamadas del contacto
POST   /api/v1/contacts/{id}/do-not-contact → Marcar como no contactar
POST   /api/v1/contacts/{id}/call      → Llamar ahora a este contacto
POST   /api/v1/contacts/{id}/send-whatsapp → Enviar mensaje manual
```

### `app/api/v1/admin.py` (requiere ADMIN_SECRET_KEY)
```
GET    /api/v1/admin/tenants            → Todos los tenants
GET    /api/v1/admin/tenants/{id}       → Detalle de tenant
PATCH  /api/v1/admin/tenants/{id}      → Modificar plan, estado
POST   /api/v1/admin/tenants/{id}/provision → Re-provisionar tenant
GET    /api/v1/admin/metrics/global    → Métricas de todo el SaaS
GET    /api/v1/admin/costs/global      → Costos totales de APIs
GET    /api/v1/admin/health            → Health check de todos los servicios
```

---

## FASE 10 — SERVICIOS DE INSTAGRAM

### `app/services/instagram/client.py`

```python
class InstagramGraphClient:
    BASE_URL = "https://graph.facebook.com/v21.0"
    
    async def send_dm(self, instagram_account_id: str, access_token: str,
                      recipient_id: str, message: str) -> dict:
        """Envía DM via Instagram Graph API"""
    
    async def publish_post(self, instagram_account_id: str, access_token: str,
                           image_url: str, caption: str) -> dict:
        """
        Proceso de 2 pasos de Instagram:
        1. POST /{account_id}/media → sube la imagen y crea media container
        2. POST /{account_id}/media_publish → publica el container
        Retorna instagram_post_id y permalink
        """
    
    async def get_post_insights(self, post_id: str, access_token: str) -> dict:
        """Obtiene likes, comments, reach de un post publicado"""
    
    async def get_oauth_url(self, tenant_slug: str) -> str:
        """Genera URL de OAuth para que el negocio conecte su Instagram"""
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Intercambia el code de OAuth por access_token de larga duración"""
```

---

## FASE 11 — DASHBOARD REACT — DISEÑO PROFESIONAL

### Diseño visual completo

**Tema:** Dashboard oscuro ejecutivo con acentos verde neón para el mercado peruano de negocios.
- Background: `#0A0F1E` (azul marino muy oscuro)
- Cards: `#111827` con borde `#1F2937`
- Accent principal: `#10B981` (verde esmeralda — representa dinero, crecimiento)
- Accent secundario: `#3B82F6` (azul — confianza, tecnología)
- Accent terciario: `#F59E0B` (ámbar — alertas, leads calientes)
- Texto: `#F9FAFB` primary, `#9CA3AF` secondary
- Fuente headings: `Syne` (Google Fonts — moderna, sin serif, tech)
- Fuente body: `Inter` (legible en dashboards de datos)
- Sidebar: `#0D1117` con items activos en `#10B981/20` y borde izquierdo verde

### `src/pages/dashboard/DashboardPage.tsx`

Layout completo:
```
┌─────────────────────────────────────────────────────┐
│  AgentePro          🟢 Sistema activo    [avatar]   │ ← TopBar
├──────────┬──────────────────────────────────────────┤
│          │  Buenos días, [nombre] ☀️               │
│ SIDEBAR  │  [fecha] — Plan: Professional           │
│          ├──────────────────────────────────────────┤
│ Dashboard│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│          │  │ 247  │ │  18  │ │  5   │ │ 1.2m │  │
│ 💬 Chats │  │ msgs │ │leads │ │citas │ │t.resp│  │
│          │  │ hoy  │ │ sem  │ │ mes  │ │ prom │  │
│ 📞 Llam. │  └──────┘ └──────┘ └──────┘ └──────┘  │
│          │                                          │
│ 👥 Cont. │  [Gráfico área — mensajes últimos 7d]   │
│          │                                          │
│ 📸 Insta │  ┌──────────────┐  ┌──────────────────┐│
│          │  │ Leads activos│  │ Posts pendientes  ││
│ ⚡ Auto. │  │ [pipeline]   │  │ de aprobación     ││
│          │  └──────────────┘  └──────────────────┘│
│ 🤖 Agente│                                          │
│          │  [Conversaciones recientes — últimas 5] │
│ ⚙️ Config│                                          │
└──────────┴──────────────────────────────────────────┘
```

Los 4 KPI cards deben tener:
- Número grande y prominente
- Ícono con color de fondo suave
- Porcentaje de cambio vs período anterior (verde si sube, rojo si baja)
- Sparkline mini (últimos 7 días)

### `src/pages/conversations/ConversationsPage.tsx`

Layout tipo WhatsApp Web exacto:
- Panel izquierdo: lista de conversaciones con filtros (canal: WS/IG, estado, lead_stage)
- Panel derecho: thread de mensajes
- Burbujas diferenciadas por tipo (cliente, IA, humano, sistema)
- Botón "Tomar Control" grande y rojo cuando el bot está activo
- Botón "Devolver a IA" cuando está en modo humano
- Indicador en tiempo real de "el agente está escribiendo..." con Socket.io
- Canal indicator (ícono WhatsApp verde o Instagram rosa)

### `src/pages/calls/CallsPage.tsx`

Lista de llamadas con:
- Ícono de dirección (entrante/saliente)
- Nombre del contacto y número
- Duración de la llamada
- Resultado (cita, info, escalada, sin interés)
- Badge de sentimiento (😊😐😟)
- Al hacer click: panel lateral con transcript completo + resumen de Claude
- Player de audio con waveform para escuchar la grabación
- Botón "Llamar de nuevo" para lanzar nueva llamada saliente

### `src/pages/contacts/ContactsPage.tsx`

Vista de pipeline visual tipo Kanban con columnas:
- ❄️ Frío (score 0-33)
- 🌤️ Tibio (score 34-66)
- 🔥 Caliente (score 67-85)
- ⭐ Cliente (score 86-100)

Drag and drop entre columnas (actualiza lead_stage via API).
Card de contacto con: avatar, nombre, teléfono, último mensaje, canal de origen.
Click en card → modal con historial completo de WhatsApp + llamadas.

### `src/pages/instagram/InstagramPage.tsx`

Calendario mensual de posts con:
- Posts publicados (verde, con contador de likes)
- Posts programados (azul, con hora)
- Posts pendientes de aprobación (ámbar, con botón aprobar/rechazar)
- Borradores (gris)

Botón "Generar posts de esta semana" → llama API → Claude + fal.ai generan 3 posts.
Preview de cada post con imagen generada y caption.
Editor inline para modificar el caption antes de aprobar.
Toggle "Auto-publicar" para que se publique sin aprobación manual.

### `src/pages/automations/AutomationsPage.tsx`

Cards por tipo de automatización con:
- Nombre y descripción
- Toggle on/off grande
- Métricas: ejecutada X veces, tasa de éxito Y%
- Configuración inline (cuántas horas esperar, mensaje template, etc.)
- Historial de últimas 10 ejecuciones

### `src/pages/agent/AgentConfigPage.tsx`

Wizard de 6 pasos con progress bar animada:

**Paso 1 — Identidad:**
- Nombre del negocio, tipo (selector con íconos grandes), nombre del agente
- Selector de personalidad con preview: card de cada opción muestra cómo respondería el agente

**Paso 2 — Horario:**
- Grid visual de lunes a domingo × horario
- Toggle por día (activo/inactivo)
- Time pickers para hora de apertura y cierre
- Preview en tiempo real: "Ahora serían las [hora]. ¿Está dentro del horario? [Sí/No]"

**Paso 3 — Servicios:**
- Tabla editable con columnas: servicio, descripción, precio (S/.)
- Agregar/eliminar filas dinámicamente
- Ordenar arrastrando

**Paso 4 — Preguntas Frecuentes:**
- Lista editable de FAQs con categorías
- Agregar/editar/eliminar/reordenar
- Import desde texto (pega tus FAQs y Claude las estructura automáticamente)

**Paso 5 — Voz:**
- Selector de voz con botón "Escuchar muestra" (reproduce audio de demo)
- Config de horario de llamadas salientes
- Guión de apertura personalizable
- Toggle para habilitar/deshabilitar llamadas salientes

**Paso 6 — Preview y prueba:**
- Chat simulado en la derecha (igual a un WhatsApp)
- Campo de texto para probar el agente en tiempo real
- Llama al endpoint `/api/v1/agent/config/test`
- Muestra la respuesta del agente con metadata (intent, confidence, lead_score)
- Botón "¡Activar agente!" para guardar y hacer live

### `src/pages/onboarding/OnboardingPage.tsx`

5 pasos visuales con íconos grandes y animaciones:

**Paso 1 — Bienvenida:** nombre del negocio, tipo, plan elegido.

**Paso 2 — WhatsApp:** instrucciones detalladas con screenshots para:
- Crear cuenta Meta Business
- Activar WhatsApp Business API en developers.facebook.com
- Crear app, agregar producto WhatsApp
- Copiar Phone Number ID y Access Token

**Paso 3 — Conecta tu número:** campos para pegar Phone Number ID + Access Token.
Botón "Verificar conexión" → hace test call al webhook.
Indicador: ✅ Conectado / ❌ Error con descripción exacta.

**Paso 4 — Configura tu agente:** versión simplificada del AgentConfigWizard (solo básicos: nombre, horario, 3 FAQs).

**Paso 5 — Listo:** confetti animation, muestra el número de teléfono asignado, link al dashboard, QR code del número de WhatsApp del negocio.

---

## FASE 12 — SOCKET.IO EN TIEMPO REAL

### Backend `app/core/socket.py`

```python
import socketio

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.FRONTEND_URL,
    logger=False,
    engineio_logger=False
)

# Eventos que el servidor emite al frontend:
# "new_message" → {conversation_id, message} — nuevo mensaje en WhatsApp
# "agent_typing" → {conversation_id} — el agente está generando respuesta
# "agent_response" → {conversation_id, message} — respuesta del agente lista
# "escalation_needed" → {conversation_id, contact_name, reason} — alerta de escalado
# "new_call" → {call_id, from_number, direction} — llamada entrante
# "call_ended" → {call_id, outcome, duration} — llamada terminada
# "lead_score_updated" → {contact_id, new_score, new_stage} — lead calificado
# "instagram_post_ready" → {post_id} — nuevo post generado listo para aprobar

# Rooms: cada tenant_id es una room separada
# El frontend se une a la room de su tenant al conectarse

@sio.on('connect')
async def on_connect(sid, environ, auth):
    """Verifica JWT del token en auth['token'] y une al tenant room"""

@sio.on('join_tenant')
async def on_join_tenant(sid, data):
    """Une el socket a la room del tenant"""
```

### Frontend `src/hooks/useSocket.ts`

```typescript
// Conecta con JWT en el handshake
// Al conectar exitosamente: se une a la room del tenant
// Handlers para cada evento:
// - new_message → invalida React Query cache de conversations
// - escalation_needed → muestra toast de notificación prominente (rojo)
// - new_call → muestra banner de llamada entrante
// - call_ended → actualiza lista de llamadas
// - instagram_post_ready → muestra notificación con link al post
// - agent_typing → muestra indicador en la conversación activa
// Reconexión automática con exponential backoff
```

---

## FASE 13 — PAGOS CON CULQI

### `app/services/culqi_service.py`

```python
class CulqiService:
    
    async def process_payment_and_provision(
        self,
        culqi_token: str,
        plan: str,
        tenant_data: dict,
        db: AsyncSession
    ) -> dict:
        """
        1. Calcula el monto según el plan:
           basic: 19900 (S/. 199.00 en centavos)
           professional: 34900
           enterprise: 54900
        2. Llama a Culqi API para cobrar el token
        3. Si pago exitoso → llama TenantProvisioner.provision_new_tenant()
        4. Crea registro de Subscription en DB
        5. Retorna confirmación con datos del tenant creado
        """
    
    async def handle_culqi_webhook(self, event: dict, db: AsyncSession):
        """
        charge.creation.success → renueva suscripción mensual
        charge.creation.fail → notifica al dueño por WhatsApp + email
        subscription.cancel → desactiva tenant con 7 días de gracia
        """
```

---

## FASE 14 — DOCKER COMPOSE

### `docker-compose.yml` — Desarrollo local completo

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: agentepro
      POSTGRES_PASSWORD: agentepro_dev
      POSTGRES_DB: agentepro
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agentepro"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: ./backend/.env
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uv run uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uv run celery -A app.workers.celery_app worker --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    restart: unless-stopped
    env_file: ./frontend/.env
    volumes:
      - ./frontend/src:/app/src
    ports:
      - "5173:5173"
    command: npm run dev -- --host

volumes:
  postgres_data:
  redis_data:
```

---

## FASE 15 — ARCHIVOS DE DEPLOY

### `backend/.env.example` — COMPLETO

```env
# ═══ APP ═══
APP_NAME=AgentePro
VERSION=2.0.0
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=cambia-esto-con-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
ADMIN_SECRET_KEY=clave-secreta-admin
FRONTEND_URL=http://localhost:5173

# ═══ BASE DE DATOS ═══
DATABASE_URL=postgresql+asyncpg://agentepro:agentepro_dev@localhost:5432/agentepro
DATABASE_URL_SYNC=postgresql://agentepro:agentepro_dev@localhost:5432/agentepro

# ═══ REDIS ═══
REDIS_URL=redis://localhost:6379/0

# ═══ ANTHROPIC ═══
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL_DEFAULT=claude-sonnet-4-6
CLAUDE_MODEL_COMPLEX=claude-opus-4-8
CLAUDE_MAX_TOKENS=1024

# ═══ META WHATSAPP ═══
META_APP_ID=
META_APP_SECRET=
META_VERIFY_TOKEN_SECRET=secreto-para-generar-tokens-por-tenant

# ═══ META INSTAGRAM ═══
META_INSTAGRAM_APP_ID=
META_INSTAGRAM_APP_SECRET=

# ═══ TWILIO ═══
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=
TWILIO_DEFAULT_PHONE_NUMBER=+51...

# ═══ RETELL AI ═══
RETELL_API_KEY=
RETELL_DEFAULT_VOICE_ID=es-ES-ElviraNeural
RETELL_WEBHOOK_SECRET=

# ═══ HUBSPOT ═══
HUBSPOT_ACCESS_TOKEN=pat-na1-...
HUBSPOT_PORTAL_ID=

# ═══ MODAL ═══
MODAL_TOKEN_ID=
MODAL_TOKEN_SECRET=

# ═══ FAL.AI ═══
FAL_KEY=

# ═══ CULQI ═══
CULQI_PUBLIC_KEY=pk_live_...
CULQI_SECRET_KEY=sk_live_...
CULQI_WEBHOOK_SECRET=

# ═══ RESEND ═══
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=noreply@agentepro.pe

# ═══ SUPABASE ═══
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_STORAGE_BUCKET=agentepro-media

# ═══ PLANES ═══
PLAN_BASIC_MESSAGES=500
PLAN_BASIC_CALLS=30
PLAN_PROFESSIONAL_MESSAGES=2000
PLAN_PROFESSIONAL_CALLS=100
PLAN_ENTERPRISE_MESSAGES=999999
PLAN_ENTERPRISE_CALLS=999999
```

### `backend/railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uv run alembic upgrade head && uv run uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### `frontend/vercel.json`

```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ]
}
```

---

## FASE 16 — TESTS ESENCIALES

### `backend/tests/test_webhook_whatsapp.py`
- Test verificación de webhook Meta (GET con hub.challenge)
- Test recepción de mensaje de texto normal
- Test de mensaje duplicado (debe ignorar silenciosamente)
- Test firma HMAC inválida (debe retornar 403)
- Test tenant inactivo (debe ignorar)
- Test tenant con límite de mensajes excedido (debe retornar mensaje de upgrade)

### `backend/tests/test_ai_agent.py`
- Test construcción del system prompt con diferentes business_types
- Test detección de intent en respuesta (FAQ, appointment, escalation)
- Test detección de señal ESCALATE
- Test parsing del bloque <!--META:...--> 
- Test manejo de error de Claude API (fallback message)
- Test límite de tokens en contexto (truncación correcta)

### `backend/tests/test_provisioning.py`
- Test provisioning completo con mocks de Twilio, Retell, HubSpot
- Test rollback cuando falla Retell (debe liberar número Twilio)
- Test rollback cuando falla HubSpot (debe eliminar agente Retell y liberar Twilio)

### `backend/tests/test_calls.py`
- Test webhook Retell call_started
- Test webhook Retell call_ended con transcript
- Test generación de resumen con Claude mock
- Test llamada saliente con verificación de horario

---

## FASE 17 — `app/main.py` COMPLETO

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.config import settings
from app.database import engine
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from app.core.exceptions import setup_exception_handlers
from app.core.socket import sio
from app.api.v1.router import api_router
from app.webhooks import meta_whatsapp, meta_instagram, retell, twilio_voice, culqi
from app.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AgentePro 2.0 starting up", version=settings.VERSION)
    # Verificar conexión a DB
    # Verificar conexión a Redis
    # Verificar que las API keys críticas están configuradas
    yield
    logger.info("AgentePro 2.0 shutting down")

app = FastAPI(
    title="AgentePro API",
    version=settings.VERSION,
    description="SaaS de automatización de negocios con IA",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
setup_exception_handlers(app)

# Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(meta_whatsapp.router, prefix="/webhooks")
app.include_router(meta_instagram.router, prefix="/webhooks")
app.include_router(retell.router, prefix="/webhooks")
app.include_router(twilio_voice.router, prefix="/webhooks")
app.include_router(culqi.router, prefix="/webhooks")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Mount Socket.io
socket_app = socketio.ASGIApp(sio, app)
```

---

## FASE 18 — README COMPLETO

El `README.md` debe incluir estas secciones:

1. **Descripción** — qué es AgentePro 2.0 y qué hace
2. **Arquitectura** — diagrama ASCII completo del sistema
3. **Prerrequisitos** — Python 3.13, Node 22, Docker, cuentas en cada servicio
4. **Setup inicial** — paso a paso desde cero hasta tener el sistema corriendo
5. **Variables de entorno** — tabla con descripción de cada variable y dónde obtenerla
6. **Guía de Meta WhatsApp API** — cómo configurar desde developers.facebook.com
7. **Guía de Retell AI** — cómo crear agentes de voz en español
8. **Guía de Twilio** — cómo comprar número peruano
9. **Guía de HubSpot** — cómo obtener el access token
10. **Guía de Modal** — cómo instalar CLI y deployar las tareas
11. **Migraciones** — cómo correr y crear nuevas migraciones
12. **Tests** — cómo correr la suite de tests
13. **Deploy** — instrucciones para Railway y Vercel
14. **Onboarding de cliente** — cómo registrar un nuevo negocio manualmente
15. **Comandos útiles** — tabla de comandos frecuentes

---

## CHECKLIST DE CALIDAD — APLICA EN CADA ARCHIVO

**Python:**
- `from __future__ import annotations` en cada archivo
- Type hints completos en todas las funciones
- Docstrings en todas las funciones y clases públicas
- Manejo de errores explícito con logging estructurado
- Tokens de Meta/Instagram/Twilio siempre encriptados en DB
- Verificación de `wa_message_id` antes de procesar (anti-duplicados)
- Rate limiting por tenant en todos los webhooks
- Validación de firmas HMAC en webhooks de Meta y Culqi

**TypeScript:**
- `"strict": true` en tsconfig — nunca `any`
- Tipos explícitos para todas las respuestas de API
- Loading states y error states en todos los componentes
- Optimistic updates donde sea posible con React Query

**Seguridad:**
- JWT verificado en cada endpoint privado
- Rate limiting en endpoints de auth (max 5 intentos/minuto)
- Sanitización de inputs del usuario antes de incluir en prompts de Claude
- Variables de entorno nunca hardcodeadas en código

---

## GENERA ESTOS ARCHIVOS ADICIONALES AL TERMINAR

### `NEXT_STEPS.md` — Guía post-build

Con estas secciones:
1. **Consola por consola** — links exactos a cada plataforma para obtener las API keys
2. **Orden de setup recomendado** — cuáles configurar primero
3. **Testing local** — cómo usar ngrok para probar webhooks localmente
4. **Primer deploy** — paso a paso en Railway y Vercel
5. **Primer cliente** — cómo onboardear al primer negocio manualmente
6. **Primeras pruebas** — checklist de qué probar antes de cobrar al primer cliente

### `PRICING.md`

Tabla de precios con:
- Precio de venta al cliente (S/. 199 / 349 / 549)
- Costo de APIs por cliente en cada plan
- Margen neto estimado
- Break-even point (cuántos clientes para cubrir costos fijos)
- Proyección a 10, 25, 50 clientes

---

## REGLAS FINALES PARA CLAUDE CODE

1. **No pares entre fases** — construye todo de corrido hasta completar el checklist final
2. **Crea archivos reales** — no pongas `# TODO: implementar` en funciones críticas
3. **El webhook de Meta es lo más crítico** — prueba mentalmente el flujo completo antes de finalizar
4. **El auto-provisioning debe tener rollback** — si falla cualquier paso externo, limpia todo
5. **Los system prompts de Claude son el producto** — hazlos lo más detallados y robustos posible
6. **Socket.io debe funcionar** — el dashboard en tiempo real es feature diferenciadora
7. **Todos los tokens de terceros van encriptados** — sin excepciones

---

## CHECKLIST FINAL — EL SISTEMA ESTÁ LISTO CUANDO:

- [ ] `docker-compose up` levanta todo sin errores en menos de 60 segundos
- [ ] GET webhook Meta retorna el hub.challenge correctamente
- [ ] Un mensaje de WhatsApp llega → Claude responde → aparece en dashboard en tiempo real
- [ ] Llamada entrante → Retell AI contesta → transcript se guarda → Claude genera resumen
- [ ] Nuevo tenant registrado → todo se provisiona automáticamente (Twilio + Retell + HubSpot)
- [ ] Post de Instagram generado → imagen creada por fal.ai → publicado via Graph API
- [ ] Lead caliente → deal creado automáticamente en HubSpot
- [ ] Automatización de follow-up → Claude genera mensaje → se envía por WhatsApp
- [ ] Dashboard muestra métricas de todos los canales
- [ ] `uv run pytest` → todos los tests pasan
- [ ] `npm run build` → build de producción sin errores TypeScript

**¡Empieza ahora! Construye el sistema completo en el orden indicado. No pares hasta completar el checklist.**

