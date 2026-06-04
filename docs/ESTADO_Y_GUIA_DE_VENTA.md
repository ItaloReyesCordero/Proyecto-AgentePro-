# AgentePro 2.0 — Estado real, cómo venderlo y cómo funcionan tus clientes

> **Documento sin suposiciones.** Todo lo de aquí está verificado leyendo el código real
> (`agentepro/backend/app/...`) el 2026-06-01. Donde algo NO está implementado, lo digo
> explícito. Donde algo es un riesgo, lo marco con ⚠️.

---

## 1. Tu cuenta de Super Admin (la tuya)

Se crea **sola** cada vez que arranca el backend (`app/core/seed.py`), leyendo `agentepro/backend/.env`:

```
Email:      italoreyescordero1@gmail.com
Contraseña: SuperAdmin2026
```

- Entras en `http://localhost:5173/login` → al ser superadmin, te redirige a `/app/admin`.
- Es **idempotente**: si ya existe ese email, no la recrea. Si cambias la clave en `.env`, **no** se actualiza la existente (tendrías que borrar el usuario o cambiarla por código).

### ⚠️ Importante — qué ES y qué NO ES tu cuenta de Super Admin

Tu cuenta de superadmin **NO es un cliente con todo activado**. Es la cuenta del **dueño de la plataforma**. Técnicamente:

- El superadmin tiene `tenant_id = NULL` (no pertenece a ningún negocio).
- Por eso **solo** ve el panel `/app/admin` (gestión de TODA la plataforma).
- **No puede** entrar al dashboard normal de un negocio (conversaciones, agente, etc.), porque esas pantallas exigen un `tenant`. El código (`get_current_tenant`) devuelve **403** si el usuario no tiene tenant.

**Conclusión:** hay dos roles distintos:
| Rol | Para qué sirve | Qué ve |
|---|---|---|
| **Super Admin (tú, como dueño de la plataforma)** | Administrar a todos tus clientes | Panel `/app/admin`: métricas globales, lista de tenants, cambiar plan, activar/desactivar, reiniciar uso |
| **Owner (cada cliente / negocio)** | Operar SU negocio | Dashboard normal: conversaciones, llamadas, contactos, agente IA, configuración |

> Si tú (Italo) también quieres operar **tu propio negocio** dentro de la plataforma (tener tus propios clientes por WhatsApp), debes **registrarte como un negocio más** (un tenant aparte, con otro email), además de tu cuenta de superadmin. Son dos cosas separadas por diseño.

---

## 2. Cómo se guardan los datos de cada cliente (multi-tenancy real)

**Modelo: una sola base de datos Postgres compartida, aislada por `tenant_id` (multi-tenant a nivel de fila).**

- **NO** hay una base de datos por cliente. Todos los clientes viven en **la misma BD** (`agentepro`), en el volumen Docker `agentepro_postgres_data`.
- Cada tabla de negocio (`contacts`, `conversations`, `messages`, `calls`, `instagram_posts`, `automations`, etc.) tiene una columna **`tenant_id`** que apunta al negocio dueño de ese dato.
- El aislamiento se hace **a nivel de aplicación**: cada endpoint del dashboard usa la dependencia `CurrentTenant`, que resuelve el `tenant_id` desde el JWT del usuario y filtra las consultas por ese id.
- Cada negocio (`tenants`) guarda **sus propias credenciales** de canales:
  - WhatsApp: `phone_number_id`, `waba_id`, y el `whatsapp_access_token` **cifrado** (Fernet).
  - Voz: `twilio_phone_number`, `retell_agent_id`.
  - Instagram: `instagram_account_id`, `instagram_access_token`.
  - HubSpot: `hubspot_company_id`.
- Cada negocio tiene un **slug único** (ej. `mi-negocio-qa-9f6cb9`) y su webhook propio: `/webhooks/whatsapp/{slug}`.

### ⚠️ Riesgos reales de este modelo (que debes conocer antes de vender)

1. ✅ **Aislamiento forzado en la capa de datos (resuelto 2026-06-01).** Antes el aislamiento dependía de que cada endpoint recordara filtrar por `tenant_id`. Ahora `app/core/tenant_scope.py` inyecta automáticamente `WHERE tenant_id = <tu negocio>` en **todas** las consultas SELECT de un negocio autenticado (incluidas relaciones/joins), vía un listener de SQLAlchemy. **Es imposible que un endpoint filtre datos de otro negocio aunque olvide el `where`.** Probado: un negocio pidiendo por id un dato de otro recibe vacío. *Capa extra pendiente:* RLS **nativo** de Postgres (rol de BD restringido), que conviene activar en el despliegue de producción.
2. **Backups son globales.** Como es una sola BD, el respaldo/restauración es de toda la plataforma, no por cliente. No hay export/borrado por cliente implementado.
3. **Escala vertical.** Todos comparten Postgres/Redis. Funciona perfecto para decenas/cientos de clientes pequeños; para escalar mucho habría que pensar en sharding o BD por cliente (no implementado).

---

## 3. Qué puedes hacer HOY — SIN ninguna API key, sin Culqi, sin pagar nada

Todo esto ya funciona solo levantando Docker (`docker compose up -d` en `agentepro/`):

✅ **La plataforma completa corre** (frontend, backend, Postgres, Redis).
✅ **Tu panel de Super Admin** (`/app/admin`): ver todos los clientes, métricas globales (tenants, contactos, mensajes, llamadas), costo estimado de Claude, estado de servicios, **cambiar el plan** de un cliente, **activar/desactivar** un cliente, **reiniciar el uso mensual**.
✅ **Registro self-service de clientes** (`/register`): porque `ALLOW_FREE_SIGNUP=true`, un cliente puede registrarse **sin pago real** (el cobro Culqi está *simulado* mientras no haya `CULQI_SECRET_KEY`). Crea automáticamente: el negocio (tenant), el usuario dueño, un AgentConfig con FAQs por defecto según el rubro, un VoiceConfig, y automatizaciones por defecto según el plan.
✅ **Onboarding del cliente** incluido el paso de "Conectar WhatsApp" (guarda las credenciales que el cliente pegue, cifradas).
✅ **Dashboard del cliente** (Owner): puede ver sus secciones, **configurar su agente IA** (nombre, FAQs, horario, mensajes), gestionar contactos, ver conversaciones/llamadas (las que existan).
✅ **Toda la lógica de datos**: contactos, conversaciones, mensajes, lead scoring (los campos), automatizaciones (definición), suscripciones (registro).

> En resumen: **puedes demostrar y vender la plataforma, dar de alta clientes y mostrarles su panel HOY mismo**, sin gastar en APIs. Lo único que NO ocurrirá sin keys es la parte "inteligente/externa" (ver abajo).

---

## 4. Qué NO funciona sin keys (y cuál es el mínimo para vender de verdad)

El código está hecho para **degradar con elegancia**: si falta una key, ese pedazo se salta o devuelve un mensaje de error controlado, **no se cae la app**. Pero la función no ocurre:

| Función | Key necesaria | Sin la key… |
|---|---|---|
| 🧠 **Respuestas de IA (el corazón)** | `ANTHROPIC_API_KEY` | El agente responde *"Disculpe, tuve un problema técnico…"*. **No hay IA real.** |
| 📲 **Recibir/responder WhatsApp real** | Credenciales Meta del **cliente** (las pega él) + `META_APP_SECRET` (tuyo, plataforma) | Sin las del cliente: no llegan mensajes. ⚠️ Sin `META_APP_SECRET`: el webhook **no verifica la firma** (acepta todo — ok en dev, **inseguro en producción**). |
| ☎️ **Llamadas de voz** | `TWILIO_*` + `RETELL_API_KEY` | El provisioning **se salta** comprar número y crear agente de voz (devuelve `None`). No hay llamadas. |
| 🖼️ **Generar contenido Instagram** | `ANTHROPIC_API_KEY` + `FAL_KEY` (imágenes) | No genera posts. |
| 🎙️ **Transcribir audios de WhatsApp** | `OPENAI_API_KEY` (Whisper) | Los audios no se transcriben. |
| 🔗 **Sincronizar CRM** | `HUBSPOT_ACCESS_TOKEN` | El provisioning se salta crear la empresa en HubSpot. |
| ✉️ **Email de bienvenida** | `RESEND_API_KEY` | No se envía el correo (es best-effort, no rompe nada). |
| 💳 **Cobro real** | `CULQI_SECRET_KEY` | Cobro **simulado**; los registros entran gratis/trial. |
| 📦 **Subida de archivos/media** | `SUPABASE_URL` + `SUPABASE_KEY` | No hay almacenamiento de media externo. |

### 🎯 El MÍNIMO para tener un producto vendible y útil

Para que un cliente reciba valor real (un agente que de verdad responde por WhatsApp), necesitas **solo dos cosas**:

1. **`ANTHROPIC_API_KEY`** (tú, una sola, a nivel plataforma) → habilita la IA para todos tus clientes. **Esto es lo único de pago imprescindible.**
2. **Credenciales de WhatsApp Business API de cada cliente** (las consigue él en Meta y las pega en su onboarding) + **`META_APP_SECRET`** tuyo para validar firmas en producción.

Con eso ya vendes "agente de WhatsApp con IA". Voz, Instagram, CRM, transcripción y cobro automático son **add-ons** que activas después con sus respectivas keys.

---

## 5. El flujo real de un cliente (lo que ya pasa en el código)

1. El cliente entra a tu landing (`/`), elige un plan y va a `/register?plan=...`.
2. Se registra (`POST /auth/register`) → se crea su negocio en **trial de 14 días** con FAQs y automatizaciones por defecto.
3. Pasa al onboarding → en el paso WhatsApp pega su `Phone Number ID` y `Access Token` (`POST /whatsapp/connect`) → se guardan cifrados y se le muestra **su webhook URL + verify token**.
4. El cliente configura ese webhook en su app de Meta. A partir de ahí, los mensajes que le escriban entran por `/webhooks/whatsapp/{su-slug}`.
5. El backend resuelve el tenant por el slug, arma el prompt con la config del agente, llama a Claude (si hay `ANTHROPIC_API_KEY`) y responde. Incrementa `messages_used_this_month`.
6. El cliente ve todo en su dashboard. Tú lo ves en tu panel de Super Admin.

**Límites y bloqueos que SÍ se hacen cumplir hoy:**
- Mensajes: en `agent.py` se bloquea al superar `PLAN_*_MESSAGES`.
- Llamadas: en `outbound_caller.py` se bloquea al superar `PLAN_*_CALLS`.
- **Expiración del trial (implementado 2026-06-01):** cuando un tenant en plan `TRIAL` pasa su `trial_ends_at`, el sistema lo bloquea: (a) el dashboard devuelve **HTTP 402 `TRIAL_EXPIRED`** y el frontend lleva al cliente a `/app/upgrade`; (b) el **agente deja de responder** WhatsApp/Instagram (el mensaje entrante sí se guarda); (c) **no se hacen llamadas salientes**. El login sigue funcionando para que el cliente vea la pantalla de renovación. Los datos quedan intactos; al cambiarle el plan a uno pagado desde tu panel de Super Admin, se reactiva.

---

## 6. Qué falta para poder vender/alquilar "en serio" (crítico y honesto)

Esto **no** está implementado y lo necesitarás según qué tan formal quieras ser:

1. ✅ **La expiración del trial YA se hace cumplir** (implementado 2026-06-01). Ver detalle en la sección 5. Para "renovar" a un cliente, cámbiale el plan a uno pagado desde tu panel de Super Admin.
2. ⚠️ **El cobro real (Culqi) no está cableado en la UI.** El registro siempre crea trial. Para cobrar de verdad hay que conectar el front al endpoint `/signup` con el widget de Culqi y poner `ALLOW_FREE_SIGNUP=false` + `CULQI_SECRET_KEY`.
3. **No hay pantalla de "subir de plan"/billing** para el cliente (el backend tiene `/subscriptions`, falta la UI). *Nota:* ya existe `/app/upgrade` (pantalla de "prueba vencida"), pero no es self-service de cambio de plan.
4. ✅ **Crear cliente desde el panel de Super Admin (implementado 2026-06-01).** Botón "Crear negocio" en `/app/admin` → `POST /admin/tenants` (sin cobro, reutiliza el provisioner). El dueño queda listo para iniciar sesión con la contraseña que definas.
5. ✅ **Export y borrado de datos por cliente (implementado 2026-06-01).** En `/app/admin`, por cada tenant: botón Exportar (`GET /admin/tenants/{id}/export` → descarga JSON sin secretos) y Eliminar (`DELETE /admin/tenants/{id}` → borra todo en cascada, irreversible).
6. **Despliegue a producción**: hoy corre en tu Docker local. Para vender necesitas un servidor con dominio público (los webhooks de Meta/Twilio exigen URL pública HTTPS). En `.env` hay que cambiar `FRONTEND_URL`, `SECRET_KEY`, `ADMIN_SECRET_KEY` y poner `DEBUG=false`, `ENVIRONMENT=production`.
7. **Seguridad antes de cobrar a terceros**: poner `META_APP_SECRET`, rotar `SECRET_KEY`/`ADMIN_SECRET_KEY`, y revisar el punto de Row-Level Security de la sección 2.

---

## 7. Tabla de todas las API keys (qué es de pago, quién la pone)

| Key | ¿De pago? | ¿Quién la pone? | Habilita |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | **Sí** (uso) | Tú (plataforma) | **IA del agente** — imprescindible |
| `META_APP_SECRET` + credenciales WhatsApp | Gratis crear app; WhatsApp tiene costos por conversación de Meta | `META_APP_SECRET`: tú. Token/Phone ID: cada cliente | WhatsApp real |
| `TWILIO_*` | Sí | Tú | Números/llamadas |
| `RETELL_API_KEY` | Sí | Tú | Agente de voz |
| `OPENAI_API_KEY` | Sí | Tú | Transcripción de audios |
| `FAL_KEY` | Sí | Tú | Imágenes de Instagram |
| `HUBSPOT_ACCESS_TOKEN` | Tiene plan free | Tú o cliente | CRM |
| `RESEND_API_KEY` | Tiene plan free | Tú | Emails |
| `CULQI_*` | Comisión por venta | Tú | Cobro real |
| `SUPABASE_*` | Tiene plan free | Tú | Almacenamiento de media |

---

## Resumen en una línea

> **Puedes empezar a mostrar y dar de alta clientes hoy sin gastar nada. Para que el producto dé valor real necesitas UNA key de pago (`ANTHROPIC_API_KEY`) + que cada cliente conecte su propio WhatsApp. Lo demás (voz, IG, CRM, cobro automático) son add-ons. Para cobrar de verdad falta: hacer cumplir el trial, cablear Culqi, y desplegar en un servidor con dominio público.**
