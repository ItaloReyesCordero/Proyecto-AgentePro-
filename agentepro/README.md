# AgentePro 2.0

Plataforma SaaS multi-tenant de automatización de negocios con IA para el mercado peruano y latinoamericano. Cada negocio recibe automáticamente un **agente de WhatsApp IA**, **agente de voz IA**, **CRM con HubSpot**, **automatizaciones**, **generador de contenido para Instagram** y un **dashboard unificado** — todo auto-provisionado al pagar.

---

## ⚖️ Autoría y derechos

**Autor y titular de los derechos:** Italo Eduardo Reyes Cordero
**Obra:** AgentePro 2.0 — programa de ordenador (software), incluyendo su código fuente backend (FastAPI/Python), frontend (React/TypeScript), arquitectura, esquema de base de datos y documentación.
**Contacto:** italoreyescordero1@gmail.com

© 2026 Italo Eduardo Reyes Cordero. Todos los derechos reservados.

Esta obra está protegida por el **Derecho de Autor** conforme al Decreto Legislativo N.º 822 (Ley sobre el Derecho de Autor del Perú) y los tratados internacionales aplicables. El software se protege como **obra literaria** (programa de ordenador) desde su creación; su registro ante el **INDECOPI – Dirección de Derecho de Autor (DDA)** constituye prueba oficial de autoría y fecha cierta.

Queda **prohibida** la reproducción, distribución, comunicación pública, modificación, descompilación, ingeniería inversa o uso comercial total o parcial de este software sin autorización escrita del autor.

> Nota legal: en el Perú el software **no se patenta** (las patentes de invención excluyen al programa de ordenador "como tal"); la vía correcta de protección y registro es el **Derecho de Autor** ante INDECOPI. Ver el paquete de registro en [`../docs/REGISTRO_INDECOPI.md`](../docs/REGISTRO_INDECOPI.md).

---

## 0. Estado actual y documentación (act. 2026-06-01)

**Listo y verificado:** backend (87 rutas, 18 tests) · frontend conectado a datos reales · multi-tenant aislado por `tenant_id` · landing pública en `/` y app en `/app/*` · **panel Super Admin** en `/app/admin` con **dashboard financiero** (MRR, ganancia/mes estimada, costo Claude real, gráficos de actividad e ingreso por plan, y por cada negocio: mensajes, llamadas, costo Claude, ingreso y ganancia) + gestión (crear/buscar/exportar/eliminar/logs/cambiar plan/activar) · **onboarding** con conexión de WhatsApp · **trial que expira y bloquea** (402 → `/app/upgrade`) + banner de días · botón "Probar agente" · **tarjeta de activación** + estado de WhatsApp en el dashboard del cliente · **toasts** en tiempo real · **buscador de contactos** · webhook de WhatsApp **rechaza firmas inválidas en producción**.

> El **Super Admin** es solo administración: su menú **únicamente** muestra el panel `/app/admin` (no ve Conversaciones/Llamadas/Contactos/Instagram/Automatizaciones/Agente IA, porque no tiene negocio propio). Si quieres operar tu propio negocio, regístralo aparte como un tenant más.

> **Panel Super Admin por módulos (2026-06-02):** el panel `/app/admin` ahora está dividido en **5 pestañas**: **Dashboard** (KPIs + gráficos + estado de servicios/API keys), **Negocios** (registrados; crear/buscar/activar-desactivar/cambiar plan/restablecer clave del dueño/exportar/eliminar/logs), **Uso y consumo** (por negocio: contactos, mensajes, llamadas, tokens, costo Claude $, ingreso y ganancia, con totales), **Cobros** (cobro manual Yape) y **Recuperación** (solicitudes de contraseña). **Bug corregido:** *Desactivar* ahora bloquea de verdad al dueño — el backend devuelve **402 `ACCOUNT_SUSPENDED`** (antes 403 sin código) y el interceptor lo lleva a `/app/upgrade`; el agente de WhatsApp/Instagram y las llamadas ya respetaban `is_active`. Guía de pruebas: **`docs/MANUAL_DE_PRUEBAS.md`**.

> **4 planes + bloqueo de módulos por plan (act. 2026-06-04):** los planes son **Inicial S/149** (200 mensajes, solo WhatsApp IA), **Basic S/249** (400 mensajes + Contactos), **Professional S/449** (1,500 mensajes + 60 llamadas + Instagram + Citas + voz) y **Enterprise S/799** (4,000 mensajes + 150 llamadas + Automatizaciones). Ya NO hay "ilimitado" (tope de uso justo). El **Trial de 14 días** da funciones de Professional con tope de prueba (200 mensajes / 10 llamadas, cuenta desde el día 1; riesgo máximo ~S/25 por prueba). Cada plan habilita ciertos **módulos**: el cerebro está en `backend/app/core/plans.py` (`plan_features`, `message_limit`, `call_limit`); el backend bloquea los routers no incluidos con **402 `FEATURE_LOCKED`** (`require_feature` en `dependencies.py`) y el **Sidebar** del frontend oculta lo que el plan no permite (`hooks/useTenant.ts`). La voz (número Twilio + agente Retell) **solo** se aprovisiona para planes con voz, y nunca se duplica (**1 agente por negocio**, editable). Nueva función **"Pasar con el dueño"**: en *Agente IA* el dueño lista los números de amigos/familiares; cuando uno escribe, el bot no responde como asistente, lo deriva al dueño y avisa (sin gastar Claude). Precios/topes en `PRICING.md` y `backend/.env`.

**Cobro manual (sin Culqi, act. 2026-06-02):** además del trial, hay **cobro mensual por adelantado vía Yape/transferencia** sin pasarela. El fundador confirma pagos y suspende morosos desde el panel (`Cobros por revisar`): `confirm-payment` mueve el vencimiento +1 mes y reactiva; `suspend-billing` bloquea (402 `PAYMENT_OVERDUE`). El negocio ve sus datos de pago en `/app/upgrade` y avisos de vencimiento en el banner. Culqi queda **inerte** (degrada solo si no hay keys), listo para activar luego. Detalle en `../docs/PLAN_COBRO_MANUAL.md`.

**Marca propia + landing premium (act. 2026-06-03):** la app usa el **logo oficial** (burbuja + corona, `frontend/public/logo_agentepro.png`) en todas partes vía el componente `components/ui/Logo.tsx`, incluido el favicon del navegador. La **landing** (`/`) es premium: nav sticky, hero con título en degradado + **demo de chat de WhatsApp animada**, badges de confianza, stats, "Listo en 3 pasos", testimonios y pricing destacado. El **dashboard** estrena banner de bienvenida con degradado y KPIs con acento de color. `npm run build` ✅.

**Falta para vender:** poner `ANTHROPIC_API_KEY` (único de pago imprescindible) → conectar WhatsApp de cada cliente → desplegar con dominio público HTTPS. Voz/IG/CRM son opcionales.

**Documentación clave (carpeta `../docs/`):**
- `PLAN_MAESTRO.md` — revisión del sistema, arquitectura de voz, UX y hoja de ruta.
- `COMO_CONSEGUIR_API_KEYS.md` — paso a paso de cada API key.
- `ESTADO_Y_GUIA_DE_VENTA.md` — cómo funcionan los clientes y cómo vender.
- `IDEAS.md` — backlog priorizado de mejoras (frontend + backend).
- `REGISTRO_INDECOPI.md` — paquete para registrar el software como obra (Derecho de Autor) en INDECOPI.
- `PLAN_COBRO_MANUAL.md` — plan del cobro manual sin Culqi (Yape/transferencia) + notificaciones.

> ⚠️ Notas reales: el **aislamiento entre clientes está forzado en la capa de datos** (`app/core/tenant_scope.py`): toda consulta SELECT de un negocio autenticado se filtra automáticamente por su `tenant_id` (imposible leer datos de otro aunque un endpoint olvide el filtro). El RLS *nativo* de Postgres (rol de BD restringido) es la capa extra para producción. En producción **debes** poner `META_APP_SECRET` (si no, el webhook acepta todo); el proyecto fija `bcrypt==4.0.1` (Docker ok; fuera de Docker no instales bcrypt 5.x o se rompe el login).

---

## 1. Descripción

AgentePro 2.0 conecta los canales del negocio (WhatsApp, Instagram, teléfono) a un motor de IA (Claude) que responde 24/7, califica leads, agenda citas y escala a humanos cuando corresponde. Toda la actividad se sincroniza con HubSpot y se visualiza en tiempo real en el dashboard vía Socket.io.

## 2. Arquitectura

```
                       ┌─────────────────────────────────────────┐
   WhatsApp (Meta) ───▶│                                         │
   Instagram (Meta) ──▶│   FastAPI backend (app.main:socket_app) │◀── Socket.io ──▶ Dashboard React
   Teléfono (Twilio) ─▶│   ├─ /api/v1/*   (REST)                 │
   Retell AI ─────────▶│   ├─ /webhooks/* (Meta, Retell, Twilio, │
   Culqi ─────────────▶│   │              Culqi)                 │
                       │   └─ servicios: AI · CRM · Voz · IG      │
                       └───────────┬───────────────┬─────────────┘
                                   │               │
                            PostgreSQL          Redis (cache + Celery)
                                   │               │
                       ┌───────────┴───┐   ┌───────┴────────┐
                       │ Modal (cron)  │   │ Celery workers │
                       │ follow-ups,   │   │ emails,        │
                       │ IG, reportes  │   │ recordatorios  │
                       └───────────────┘   └────────────────┘

   Externos: Anthropic (Claude) · HubSpot · fal.ai · Supabase Storage · Resend
```

## 3. Prerrequisitos

- Python 3.13 + [`uv`](https://docs.astral.sh/uv/)
- Node 22+ / npm
- Docker + Docker Compose
- Cuentas: Anthropic, Meta (WhatsApp + Instagram), Twilio, Retell AI, HubSpot, Modal, fal.ai, Supabase, Culqi, Resend

## 4. Setup inicial

```bash
# 1. Clonar y entrar
cd agentepro

# 2. Backend
cd backend
cp .env.example .env          # completa tus claves
uv sync                       # instala dependencias

# 3. Levantar Postgres + Redis (o usa docker-compose)
docker compose up postgres redis -d   # desde la raíz

# 4. Migraciones
uv run alembic upgrade head

# 5. Servidor (FastAPI + Socket.io)
uv run uvicorn app.main:socket_app --reload --port 8000

# 6. Frontend (en otra terminal)
cd ../frontend
cp .env.example .env
npm install --legacy-peer-deps
npm run dev
```

O todo de una vez:

```bash
docker compose up --build
```

## 5. Variables de entorno

Ver `backend/.env.example`. Las más importantes:

| Variable | Descripción | Dónde obtenerla |
|---|---|---|
| `SECRET_KEY` | Clave para JWT y cifrado Fernet | `openssl rand -hex 32` |
| `ADMIN_SECRET_KEY` | Protege endpoints `/api/v1/admin/*` y provisioning | la defines tú |
| `DATABASE_URL` | Postgres async (`postgresql+asyncpg://...`) | Supabase / Railway |
| `DATABASE_URL_SYNC` | Postgres sync (para Alembic) | igual sin `+asyncpg` |
| `ANTHROPIC_API_KEY` | Motor IA (Claude) | console.anthropic.com |
| `META_APP_SECRET` | Firma de webhooks de WhatsApp/Instagram | developers.facebook.com |
| `META_VERIFY_TOKEN_SECRET` | Genera tokens de verificación por tenant | la defines tú |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | Compra/config de números | console.twilio.com |
| `RETELL_API_KEY` | Agente de voz | dashboard.retellai.com |
| `HUBSPOT_ACCESS_TOKEN` | CRM | App privada en HubSpot |
| `FAL_KEY` | Generación de imágenes IG | fal.ai |
| `CULQI_SECRET_KEY` | Cobros (Perú) | culqi.com |
| `RESEND_API_KEY` | Emails transaccionales | resend.com |
| `OPENAI_API_KEY` | Whisper (transcripción de audios) | platform.openai.com |

## 6. Guía de Meta WhatsApp API

1. En [developers.facebook.com](https://developers.facebook.com) crea una app tipo **Business**.
2. Agrega el producto **WhatsApp** y obtén el `Phone Number ID` y un `Access Token`.
3. En **Configuración → Webhooks**, usa la URL: `https://TU_BACKEND/webhooks/whatsapp/<tenant_slug>`.
4. El **Verify Token** es el `webhook_verify_token` del tenant (visible en *Configuración* del dashboard).
5. Suscríbete a los campos `messages`.

## 7. Guía de Retell AI

El auto-provisioning crea el LLM (con Claude) y el agente de voz automáticamente al dar de alta un tenant. Solo necesitas tu `RETELL_API_KEY`. El número de Twilio se enruta a Retell vía TwiML en `/webhooks/twilio/voice/<slug>`.

## 8. Guía de Twilio

El provisioning compra un número (`available_phone_numbers('PE')`, con fallback a US) y configura su webhook de voz. Requiere `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN`.

## 9. Guía de HubSpot

Crea una **App privada** en HubSpot con scopes de CRM (contacts, deals, tasks, notes) y copia el token en `HUBSPOT_ACCESS_TOKEN`.

## 9b. Guía de Notion (CRM / catálogo)

Cada negocio puede conectar una base de datos de **Notion** con sus servicios y precios.
Al sincronizar, el catálogo se vuelca en `agent_config.services` (lo que lee el agente).
Es **por tenant** (cada cliente conecta su propia Notion), el token se guarda cifrado y la
sincronización ocurre al conectar y al pulsar "Sincronizar ahora" (no en cada mensaje).
Endpoints: `GET/POST /api/v1/notion/{status,connect,sync,disconnect}`. UI: Configuración →
tarjeta "CRM en Notion". Guía paso a paso para el dueño/cliente: **`docs/GUIA_NOTION_CRM.md`**.

## 10. Guía de Modal

```bash
pip install modal
modal token new
modal secret create agentepro-secrets DATABASE_URL=... ANTHROPIC_API_KEY=... # etc.
modal deploy app/modal_tasks/follow_up_leads.py
modal deploy app/modal_tasks/instagram_scheduler.py
modal deploy app/modal_tasks/weekly_reports.py
```

## 11. Migraciones

```bash
uv run alembic upgrade head            # aplica
uv run alembic revision -m "mi cambio" # nueva (autogenerate con --autogenerate)
uv run alembic downgrade -1            # revierte
```

## 12. Tests

```bash
cd backend
uv run pytest            # o: python -m pytest -q
```

**51 tests del backend** pasan (httpx `AsyncClient` + SQLite en memoria; el harness no
necesita Postgres ni `uv`). Cubren: autenticación y recuperación de contraseña,
provisioning, llamadas, agente IA, seguridad/rate-limit y **webhooks de extremo a
extremo** (`tests/test_webhook_integration.py`): handshake GET de Meta
(WhatsApp/Instagram), verificación de firma `X-Hub-Signature-256`, TwiML de Twilio
(rechazo vs. `<Stream>` a Retell) y eventos de Culqi (renovación/fallo/cancelación).
El frontend usa **Vitest** (`cd frontend && npm test`, 8 tests).

> Nota: `tests/test_webhook_integration.py` ejercita `request.form()` de Twilio, que
> requiere `python-multipart` (ya está en `pyproject.toml` y en la imagen Docker).

## 13. Deploy

- **Backend → Railway:** usa `backend/railway.json` (Dockerfile + `alembic upgrade head` en el start command).
- **Frontend → Vercel:** usa `frontend/vercel.json` (framework Vite, SPA rewrites).
- **Workers/Beat → docker-compose.prod.yml**.

## 13b. Backups de la base de datos

El servicio `backup` del `docker-compose.yml` hace **copias automáticas de Postgres**
(`pg_dump` formato custom) cada día, las guarda en `agentepro/backups/` y **rota** las
antiguas. Detalle completo en [`scripts/README.md`](scripts/README.md).

```bash
docker compose up -d backup                 # arranca el servicio (backup al iniciar + diario)
docker compose logs -f backup               # ver "Backup OK: ..."
docker compose exec backup sh /scripts/backup_db.sh                      # backup manual
docker compose exec backup sh /scripts/restore_db.sh /backups/ARCHIVO.dump   # restaurar
```

**Copia off-site a Supabase Storage** (ante pérdida del servidor entero): define
`SUPABASE_URL` y `SUPABASE_SERVICE_KEY` (clave `service_role`) en `agentepro/.env`
(dev) o `backend/.env` (prod) y crea un bucket privado `db-backups`. Cada backup se
sube solo; recupera con `download_supabase.sh list|<archivo>`. Detalle en
[`scripts/README.md`](scripts/README.md).

## 14. Onboarding de un cliente

Tres formas:
1. **Cliente solo (self-service):** se registra en `/register` → onboarding → conecta WhatsApp. Entra en trial de 14 días.
2. **Tú desde el panel Super Admin:** `/app/admin` → botón **"Crear negocio"** (define dueño, plan y contraseña inicial). El dueño ya puede iniciar sesión.
3. **Por API:** `POST /api/v1/admin/tenants` (con tu sesión de superadmin) o `POST /api/v1/provision` (con `X-Admin-Key`).

Luego el cliente configura el agente en *Agente IA* y lo prueba con **"Probar agente"** (requiere `ANTHROPIC_API_KEY`).

**Gestión de clientes (Super Admin):** cambiar plan, activar/desactivar, **exportar** datos (JSON sin secretos) y **eliminar** (borra todo en cascada). "Renovar" un trial vencido = cambiarle el plan a uno pagado.

## 15. Comandos útiles

| Comando | Acción |
|---|---|
| `uv run uvicorn app.main:socket_app --reload` | Servidor dev |
| `uv run alembic upgrade head` | Migrar DB |
| `uv run celery -A app.workers.celery_app worker` | Worker Celery |
| `uv run pytest` | Tests |
| `npm run dev` | Frontend dev |
| `npm run build` | Build de producción |
| `docker compose up --build` | Todo el stack local |

---

© 2026 **Italo Eduardo Reyes Cordero** — Todos los derechos reservados. Obra protegida por Derecho de Autor (D. Leg. N.º 822). Uso, copia o distribución no autorizada está prohibida.

Hecho con 💚 para los negocios del Perú.
