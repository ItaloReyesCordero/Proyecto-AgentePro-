# Handoff — AgentePro 2.0

> Documento de traspaso para retomar el trabajo rápido. Última actualización: 2026-06-02 (panel admin por módulos + fix activar/desactivar).

---

> **Citas automáticas + avisos + recordatorios (2026-06-03):** NUEVA feature grande. El agente detecta solo cuando un cliente pide cita (WhatsApp/Instagram/llamada), la registra, avisa al dueño (panel + email Resend + WhatsApp) y recuerda al cliente antes (tarea `beat` cada hora). Backend: modelo `appointments` (migración `006_appointments`, enums en MAYÚSCULA por consistencia con SQLAlchemy), `appointment_service.maybe_create_from_agent`, enganche en webhook_handler (chat) y call_handler (voz), API `/api/v1/appointments`, recordatorios en `reminder_tasks._send_reminders`. Se añadió servicio `beat` al `docker-compose.yml`. Envío WhatsApp unificado (Meta o Twilio) en `sender.build_outbound_client`. Frontend: página **Citas** (`/app/appointments`) + ítem en sidebar. **Verificado en vivo:** WhatsApp "quiero cita de solo barba el viernes 5pm" → cita creada (Carlos/Solo barba/2026-06-06 17:00). Límites: no revisa choques de horario ni Google Calendar (registra lo pedido; el dueño confirma). **532 tests verdes**, build ✅. Guía: `docs/GUIA_CITAS.md`. Detalle en [[agentepro-build]].

> **Voz Retell arreglada + WhatsApp probado en vivo (2026-06-03):** Al probar la 1ª llamada se hallaron y arreglaron **3 bugs reales** que rompían la creación del agente de voz (fallaba en silencio, por eso ningún tenant tenía `retell_agent_id`): (1) modelo `claude-opus-4-8`→Retell exige sus nombres, nueva setting `RETELL_LLM_MODEL=claude-4.6-sonnet`; (2) voz `es-ES-ElviraNeural` inválida→`cartesia-Hailey-Spanish-latin-america` (config.py + `backend/.env`); (3) `ambient_sound="office"` inválido→`None`. Agente de la barbería creado OK (`agent_5f5cd078...`). Probar voz sin comprar número: Retell dashboard→Agents→María→Test (web call). **WhatsApp por Twilio sandbox CONFIRMADO funcionando** (el dueño: "ya respondió"): cloudflared + webhook sandbox a `/webhooks/twilio/whatsapp/barberia-don-pepe-af0a24` + Anthropic con saldo + Notion (4 servicios) → respondió con precios reales (corte S/25). 524 tests verdes. Detalle en [[agentepro-build]].

> **CRM en Notion (2026-06-03):** NUEVO módulo. Cada negocio conecta una base de datos de Notion (servicios/precios) que se sincroniza al catálogo del agente (`agent_config.services`). Backend: 3 columnas en `tenants` (`notion_api_key` cifrado, `notion_database_id`, `notion_last_synced_at`, migración `005_notion_crm`), servicio `app/services/notion/` (`notion_client.fetch_catalog` parsea cualquier tipo de propiedad de Notion de forma flexible + `notion_sync.sync_tenant_catalog`), router `GET/POST /api/v1/notion/{status,connect,sync,disconnect}`. Frontend: tarjeta "CRM en Notion" en Configuración (`components/settings/NotionSettings.tsx`). Sincroniza al conectar y con "Sincronizar ahora" (NO hay llamadas a Notion por mensaje). **524 tests verdes** (+7 `test_notion.py`), build ✅. También se neutralizó `RETELL_WEBHOOK_SECRET` en `conftest.py` (2 tests del webhook Retell fallaban por el `.env` local, no por bug). Guía del dueño: `docs/GUIA_NOTION_CRM.md`. **Aclaración:** el agente de Retell SÍ se auto-crea, pero solo vía el provisioner (botón "Crear negocio" del panel admin o endpoints `/signup` / `/provision`), NO vía `/auth/register` (registro libre, a propósito: cada provisioning compra un número Twilio = costo real).

> **Despliegue (2026-06-03):** Stack autocontenido para UN VPS listo: `docker-compose.deploy.yml` (Caddy HTTPS auto + frontend nginx + backend + worker + beat + postgres + redis + backup), `frontend/Dockerfile` (prod), `frontend/nginx.conf`, `Caddyfile`. Un solo comando: `docker compose -f docker-compose.deploy.yml up -d --build`. Verificado: compose válido + build prod del frontend OK. Guía paso a paso para el dueño (Porkbun + Hetzner/DigitalOcean): `docs/GUIA_DESPLIEGUE_PASO_A_PASO.md`. El dueño ejecuta VPS/dominio; nosotros guiamos.

> **Último cambio (2026-06-03):** (1) **Costo REAL por negocio** en "Uso y consumo": ya no es el estimado fijo S/48 — ahora se calcula con consumo medido (Claude por tokens + voz por segundos de llamada + WhatsApp por conversaciones), columna "Costo real" + KPI "Costo real total/mes" + ganancia real. Tarifas por unidad ajustables en config.py (`RETELL_USD_PER_MIN`, `TWILIO_USD_PER_MIN`, `WHATSAPP_USD_PER_CONVERSATION`). Sale 0 hasta que haya tráfico real. (2) **Páginas legales públicas** `/privacidad` y `/terminos` (Meta las exige para WhatsApp; cubren Ley 29733, datos de Meta, 14 días gratis + pago Yape adelantado), enlazadas en el footer. 517 tests verdes, build ✅, privacy verificada por screenshot. Falta (lo hace Italo): VPS+dominio+HTTPS y poner las API keys.

> **Cambio previo (2026-06-02):** Panel Super Admin reorganizado en **5 módulos/pestañas** (Dashboard · Negocios · Uso y consumo · Cobros · Recuperación). **Bug corregido:** el botón *Desactivar negocio* ahora bloquea de verdad al dueño — backend devuelve `402 ACCOUNT_SUSPENDED` y el front lo redirige a `/app/upgrade` (antes era 403 sin código y react-query dejaba el panel a medias). Sistema verificado en vivo: todos los endpoints 200, 517 tests en verde. **Pendiente #1 para producción: configurar API keys** (todas en `false`; sin `ANTHROPIC_API_KEY` el agente IA no responde). Manual de pruebas manuales: **`docs/MANUAL_DE_PRUEBAS.md`**.

---

## 1. Objetivo del proyecto

**AgentePro 2.0** es un **SaaS multi-tenant de automatización de negocios con IA**, pensado para negocios peruanos 🇵🇪. Cada negocio (tenant) obtiene un agente que:

- Atiende **WhatsApp** 24/7 (responde, califica leads, agenda citas).
- Hace y contesta **llamadas de voz** en español (Twilio/Retell).
- Genera **contenido de Instagram** con IA (imagen + texto).
- Lleva **CRM automático** (sincroniza con HubSpot).
- Corre **automatizaciones** (seguimientos, recordatorios, reportes).
- Todo visible en un **dashboard unificado** en tiempo real.

Modelo de negocio: planes de suscripción (Inicial S/149, Basic S/249, Professional S/449, Enterprise S/799) con prueba gratis de 14 días y bloqueo de módulos por plan.

**Stack:**
- **Backend:** FastAPI + Socket.io, SQLAlchemy async, Postgres (Docker), Redis, Alembic. Carpeta `agentepro/backend/app`.
- **Frontend:** React 19 + Vite + TypeScript + TailwindCSS + react-router-dom 7 + Zustand + TanStack Query. Carpeta `agentepro/frontend`.
- **Infra:** Docker Compose (`agentepro/docker-compose.yml`) — servicios: frontend (5173), backend (8000), worker, postgres (5432), redis (6379).
- Spec completa de producto: `PROMPT_MAESTRO_AGENTEPRO_2.0.md`.

---

## 2. Estado actual

- ✅ **Backend completo y verificado** (modelos, schemas, services, webhooks, api/v1, workers, alembic). **85 rutas**, **51 tests pasan**.
- ✅ **Frontend completo y conectado a datos reales** (las páginas usan hooks que llaman a la API; no son cascarones).
- ✅ **Verificado end-to-end** con navegador/API real: landing → registro → onboarding (WhatsApp) → dashboard; superadmin → panel `/app/admin`; bloqueo de trial; crear/exportar/eliminar negocio.
- ✅ **Panel Super Admin** (`/app/admin`): métricas, **crear negocio**, cambiar plan, activar/desactivar, **exportar** (JSON sin secretos), **eliminar** (cascada), reiniciar uso.
- ✅ **Trial que expira y bloquea** (2026-06-01): dashboard 402 → `/app/upgrade`, el agente deja de responder, no hay llamadas. Banner de días restantes en el dashboard.
- ✅ **Docker corriendo** — contenedores de `agentepro` arriba (+ nuevo servicio `backup`).
- ✅ **Backups automáticos de Postgres** (2026-06-01): servicio `backup` en el compose (`pg_dump` diario, rotación, restore). **Verificado en runtime** (ver §8).
- ✅ **Aislamiento multi-tenant** forzado en la capa de datos (RLS de aplicación) — verificado.
- ✅ **Tests de webhooks de extremo a extremo** (2026-06-01): `tests/test_webhook_integration.py` (+19, total **51**) pega a los endpoints reales `/webhooks/*` — handshake GET de Meta (WhatsApp/Instagram), firma `X-Hub-Signature-256`, TwiML de Twilio (rechazo vs. `<Stream>` a Retell) y eventos de Culqi (renovación/fallo/cancelación de suscripción).
- ⚠️ **Pendiente de decisión:** cobro real Culqi no cableado en UI (todo entra como trial); IA apagada hasta poner `ANTHROPIC_API_KEY`.

**Documentos clave en `docs/`:** `PLAN_MAESTRO.md`, `COMO_CONSEGUIR_API_KEYS.md`, `ESTADO_Y_GUIA_DE_VENTA.md`, `IDEAS.md` (backlog priorizado).

---

## 3. Archivos en los que se está trabajando

Todos bajo `agentepro/frontend/src/`:

| Archivo | Rol |
|---|---|
| `router.tsx` | Routing: `/` landing pública, app movida a `/app/*`, guard de superadmin para `/app/admin`. |
| `pages/landing/LandingPage.tsx` | Landing de marketing (hero, features, pricing con `?plan=`). |
| `pages/auth/RegisterPage.tsx` | Registro; lee `?plan=` y muestra badge del plan. |
| `pages/auth/LoginPage.tsx` | Login; redirige a `/app` (o `/app/admin` si superadmin). |
| `pages/onboarding/OnboardingPage.tsx` | Onboarding 4 pasos; paso 2 conecta WhatsApp vía `/whatsapp/connect`. |
| `pages/admin/AdminPage.tsx` | **NUEVO** — panel super admin (`/app/admin`): métricas globales, costos, salud de servicios, tabla de tenants con cambio de plan + activar/desactivar + reset de uso. |
| `components/layout/Sidebar.tsx` | Nav a `/app/*` + link condicional "Super Admin". |
| `components/layout/TopBar.tsx` | Títulos por ruta `/app/*`. |
| `lib/api.ts` | Cliente axios + helper **`apiErrorMessage()`** (ver sección 4). |

Backend relevante (sin cambios esta tanda, solo de referencia): `app/api/v1/auth.py`, `app/api/v1/admin.py`, `app/api/v1/whatsapp.py`, `app/api/v1/provisioning.py`, `app/core/seed.py`.

---

## 4. Qué ha cambiado (acumulado)

1. **Routing:** `/` landing pública; app bajo **`/app/*`**; `/app/admin` (superadmin) y `/app/upgrade` (prueba vencida). Sidebar/TopBar/redirects actualizados.
2. **Signup + plan:** `RegisterPage` lee `?plan=` y lo reenvía a `/onboarding?plan=` (hoy informativo; todo entra en trial).
3. **Panel Super Admin** (`AdminPage`): métricas, **crear negocio** (`POST /admin/tenants`), cambiar plan, activar/desactivar, **exportar** (`GET /admin/tenants/{id}/export`, sin secretos), **eliminar** (`DELETE`, cascada), reiniciar uso.
4. **Onboarding** conecta WhatsApp real (`POST /whatsapp/connect`).
5. **Bloqueo de trial:** `Tenant.is_trial_expired`; `get_current_tenant` lanza 402 `TRIAL_EXPIRED`; el agente (`webhook_handler`) y las llamadas (`outbound_caller`) se bloquean; frontend redirige a `/app/upgrade` (`UpgradePage`); `TrialBanner` avisa días restantes.
6. **Fix:** `apiErrorMessage()` en `lib/api.ts` aplana el `detail` array de los 422 (antes crasheaba React). Usado en Login/Register/Onboarding/Admin.

> El build (`npm run build`) pasa. Backend importa con 85 rutas.

**Archivos nuevos clave:** `pages/admin/AdminPage.tsx`, `pages/upgrade/UpgradePage.tsx`, `components/layout/TrialBanner.tsx`, `components/common/ActivationCard.tsx`, `lib/api.ts` (helper). Backend: `admin.py` (4 endpoints: crear/export/delete/webhooks), `models/tenant.py` (property), `core/exceptions.py` (`TrialExpiredError`), `dependencies.py`, `services/whatsapp/webhook_handler.py`, `services/voice/outbound_caller.py`, `webhooks/meta_whatsapp.py` (firma).

7. **Tanda "⭐ quick wins sin keys" (2026-06-01):** tarjeta de activación + estado de WhatsApp en el dashboard (`ActivationCard`), checklist de pasos, **toasts** en `useSocket` (mensaje entrante de cliente + escalado), **buscador de contactos** (`ContactsPage`), **buscar clientes** + **modal de logs de webhooks** en `AdminPage` (`GET /admin/tenants/{id}/webhooks`), y endurecido el **webhook de WhatsApp** (`_verify_signature` rechaza si falta `META_APP_SECRET` en producción).

8. **Super Admin solo-administración + dashboard financiero (2026-06-01):** el Super Admin ya **no ve los módulos de negocio** (Conversaciones/Llamadas/Contactos/Instagram/Automatizaciones/Agente IA/Configuración). `Sidebar` solo muestra "Super Admin"; `AppLayout` redirige cualquier ruta `/app/*` (salvo `/app/admin`) a `/app/admin` si el rol es superadmin; `TopBar` oculta "Perfil"; `SettingsPage` ya no se queda cargando (maneja error). Nuevo endpoint `GET /admin/analytics` (por negocio: contactos/mensajes/llamadas/tokens/costo Claude real + ingreso/costo/ganancia por plan; totales MRR y ganancia/mes; series mensuales; conteo por plan). Precios/costos en `config.py` (`PLAN_*_PRICE`, `PLAN_*_COST_EST`, de `PRICING.md`). `AdminPage` reescrito con KPIs + gráficos (recharts) + tabla financiera por negocio, conservando toda la gestión. Verificado en runtime (crear Professional → MRR 349 / ganancia 196). 87 rutas.

9. **Aislamiento multi-tenant forzado en la capa de datos (2026-06-01):** `app/core/tenant_scope.py` — listener `do_orm_execute` que con `with_loader_criteria` inyecta `tenant_id = <sesión>` en TODA consulta SELECT de los modelos con dueño, cuando `session.sync_session.info["tenant_id"]` está puesto. Se activa en `get_current_tenant` (`set_session_tenant(db, tenant.id)`). Sesiones sin contexto (login, webhooks, workers, panel admin) NO se restringen (resuelven el tenant explícitamente). Probado en SQLite (fuga cross-tenant → vacío) y contra Postgres real (negocio normal sigue 200, sin regresión; se creó/borró un negocio de prueba). Es la "RLS de aplicación".

10. **Backups automáticos de Postgres (2026-06-01):** servicio **`backup`** en `docker-compose.yml` (y `.prod.yml`) con imagen `postgres:16-alpine`. Corre `scripts/backup_loop.sh` → backup al arrancar + cada `BACKUP_INTERVAL_SECONDS` (def. 1 día) vía `scripts/backup_db.sh` (`pg_dump --format=custom`, rotación por `BACKUP_RETENTION_DAYS`). Copias en `agentepro/backups/` (gitignored). Restore con `scripts/restore_db.sh ARCHIVO.dump`. Conexión por `PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE`. **Scripts en LF** (corren en Alpine). Doc: `scripts/README.md`, README §13b, docs/10. **Verificado en runtime:** levanté `postgres`+`backup`, se creó un `.dump` real (58 KB), `pg_restore --list` muestra todas las tablas, backup manual OK, guard del restore OK (exit 2 sin arg), y **restauración completa exit 0**.

15. **Tests de integración auth/recuperación (2026-06-01):** **32 tests backend** (+7 de integración HTTP en `tests/test_auth_integration.py`). Harness: **pytest-asyncio + httpx ASGITransport + SQLite en memoria** (StaticPool en `database.py` solo para sqlite, evita "disk I/O error"; Postgres intacto). `conftest.py` da un fixture `client` (BD limpia por test) y `ADMIN_HEADERS` (X-Admin-Key). Cubre: registro→login, login malo (401 español), flujo completo de recuperación (sin fuga, listar, aprobar→clave nueva entra/vieja no, lista vacía), dedup, admin sin auth (403), reset directo, y superadmin no recuperable. Dockerfile ahora instala las deps de test. **Cobertura backend 38% → 53%.** `RATE_LIMIT_ENABLED` configurable (off en tests).

14. **Endurecimiento tests + rate-limit (2026-06-01):** backend **25 tests pasando** (antes 18 con 2 rojos; los rojos eran de firma de webhook por `META_APP_SECRET` vacío en el contenedor — `conftest.py` ahora fuerza los secretos). Nuevos tests unitarios de `generate_temp_password` y del limitador. **Rate-limit consolidado en un solo sistema** (`RateLimitMiddleware`): ahora cubre también `/auth/password-reset-request` y NO se abre si Redis cae (fallback en memoria `app/core/rate_limit.py`). Verificado: 6º intento → 429. **Frontend: Vitest + jsdom** (`npm test`) con 8 tests (antes 0). **Cobertura backend sigue ~38%** (servicios/webhooks/workers sin tests); faltan tests de integración HTTP de auth/recuperación (flujos verificados a mano). `npm run build` ✅.

19. **Conexión WhatsApp por TWILIO (NUEVO canal, 2026-06-03):** El dueño NO quería depender de Meta (su cuenta de Meta quedó BLOQUEADA, error 131031 "Business Account locked"). Se agregó soporte para **WhatsApp vía Twilio** (su Sandbox funciona al instante, sin Meta): nuevo `backend/app/services/whatsapp/twilio_whatsapp_client.py` (envía por la API REST de Twilio, misma interfaz que el cliente de Meta), nuevo webhook `POST /webhooks/twilio/whatsapp/{slug}` (`backend/app/webhooks/twilio_whatsapp.py`, parsea el form de Twilio → ParsedWhatsAppMessage y responde desde el mismo número), y `handle_inbound_message` ahora acepta `client_override` para usar el cliente de Twilio en el mismo pipeline. **BUG REAL encontrado y arreglado** gracias a la prueba: `prompt_builder.py`/`voice_prompt_builder.py` formateaban el precio con `:.2f` asumiendo número → si el negocio pone el precio como texto ("S/25") reventaba (`Unknown format code 'f' for object of type 'str'`); ahora maneja número o texto. **Verificado end-to-end local:** un WhatsApp simulado por Twilio entró, Claude respondió con precios/horarios/dirección correctos. 31 tests en verde. Webhook de Twilio para el Sandbox: `https://<túnel>/webhooks/twilio/whatsapp/barberia-don-pepe-af0a24`. Pasos del Sandbox en `docs/_PRUEBA_WHATSAPP_LOCAL.md`. La verdad dicha al dueño: Twilio igual usa Meta por debajo, pero Twilio gestiona eso (sin bloqueos para el dueño).

18. **Prueba de WhatsApp en LOCAL con túnel (2026-06-03):** Para probar WhatsApp sin desplegar, se usa un **túnel cloudflared** (descargado en `tools/cloudflared.exe`) que expone el backend local (`localhost:8000`) en una URL pública `*.trycloudflare.com` — necesario porque Meta no alcanza `localhost`. Se dejó montado el negocio de prueba **"Barbería Don Pepe"** (usuario `pepe-wa-test@example.com`/`PepeTest123`, slug `barberia-don-pepe-af0a24`) con WhatsApp conectado (número de prueba de Meta + token temporal) y el Agente IA configurado (servicios/FAQs de barbería). Webhook verificado vía túnel (GET challenge OK). Datos y pasos en `docs/_PRUEBA_WHATSAPP_LOCAL.md`. El dueño debe configurar el webhook en Meta (Callback URL del túnel + verify token + suscribir `messages`) y escribirle al número de prueba desde su celular. **Avisos:** túnel/Docker deben seguir encendidos; la URL del túnel cambia al reiniciar; el token de Meta caduca en ~24h. Lo estable = desplegar en Railway.

17. **Despliegue Railway + guía "para bebé" + estado de APIs (2026-06-03):** El dueño eligió **Railway** (dominio `tuagentepro.xyz`). Se adaptó el código a un **único servicio web** (el backend FastAPI sirve también el frontend compilado, mismo origen): `backend/app/main.py` sirve el SPA desde `FRONTEND_DIST_DIR` (default `/app/frontend_dist`); `backend/app/config.py` normaliza la `DATABASE_URL` cruda de Railway a async/sync; nuevo `agentepro/Dockerfile.railway` (multi-stage: compila el front y lo copia al backend). Verificado localmente (SPA+API+assets 200 en un puerto). Guías: `docs/GUIA_DESPLIEGUE_RAILWAY.md` (técnica) y **`docs/EMPEZAR_AQUI_PASO_A_PASO.md`** (la importante: explicación "como a un bebé" de cada API, qué falta, y el camino a producción). **WhatsApp:** el dueño se frustró/bloqueó (spam por registrar su número). Aclarado: para PROBAR se usa el **número de prueba gratis de Meta** (sin verificar su número); el método "no oficial" tipo QR que vio en otro lado va contra ToS (riesgo de ban). `META_APP_ID/SECRET` SÍ son necesarios para WhatsApp oficial. **Notion:** el dueño quiere Notion como CRM/base de conocimiento del negocio; NO está construido (no hay nada de Notion en el código). Se le explicó que NO bloquea producción (lo que ofrece el negocio ya se configura en el panel "Agente IA"; el CRM interno ya existe) y que se construye DESPUÉS de salir en vivo. **Claves puestas:** Anthropic (falta saldo), Twilio, Retell, FAL, Resend. **Faltan:** Meta (WhatsApp). **A corregir:** SUPABASE_URL tiene una key en vez de la URL; RESEND_FROM_EMAIL ya cambiado a onboarding@resend.dev. NO se necesita OpenAI/Modal/Culqi/HubSpot.

16. **Renombre a "AgentePro" + logo inline + Docker dev + documentos INDECOPI completos (2026-06-03):** La marca pasa a **"AgentePro"** (una palabra, sin "2.0") en TODA la UI y documentos. El **logo** ahora es SVG **en línea** en `Logo.tsx` (export `LogoMark`) para que SIEMPRE se vea: en el contenedor de desarrollo el `public/` no se montaba, por eso el logo "no se veía" en localhost:5173. Se añadieron al `docker-compose.yml` los montajes de `./frontend/public` e `./frontend/index.html` y se recreó el contenedor (`docker compose up -d frontend`): verificado en vivo el logo del bot, el título "AgentePro" y el demo del celular (chat + llamada). **Documentos para INDECOPI (en `docs/`):** `Memoria_Descriptiva_AgentePro.docx`, `Manual_de_Usuario_AgentePro.docx`, `Plan_de_Pruebas_de_Software_AgentePro.docx`, `Codigo_Fuente_AgentePro.zip`, y en `docs/documentacion1 al 6/` los 6 documentos rellenados ("Documento N - … - AgentePro.docx"; el 5 adaptado a titularidad de persona natural porque el autor no tiene empresa/RUC). Falta solo completar DNI/domicilio/teléfono del autor. Sin "2.0" ni faltas (validado). `npm run build` ✅.

16. **4 planes + bloqueo de módulos por plan + candado Retell + "pasar con el dueño" (2026-06-04):** El dueño analizó los costos reales (Claude ~S/0.05/msg, Retell ~S/1.5/llamada) y rediseñó el modelo: **4 planes** — **Inicial S/149** (200 msg, solo WhatsApp IA), **Basic S/249** (400 msg + Contactos), **Professional S/449** (1,500 msg + 60 llamadas + Instagram + Citas + voz), **Enterprise S/799** (4,000 msg + 150 llamadas + Automatizaciones). Se eliminó el "ilimitado" (tope de uso justo). **Trial 14 días = funciones de Professional con tope de prueba 200 msg / 10 llamadas** (cuenta desde el día 1; riesgo máx ~S/25). Backend: nuevo `PlanType.INICIAL` (migración `007_inicial_plan`), cerebro central `app/core/plans.py` (`plan_features`/`message_limit`/`call_limit`), excepción `FeatureNotInPlanError` (402 `FEATURE_LOCKED`) + `require_feature` aplicado a los routers `contacts/instagram/appointments/calls/voice/automations`; topes de msg/llamadas desde el cerebro central; citas-auto y llamada entrante también chequean plan+tope. **Candado Retell**: la voz (Twilio+Retell) solo se aprovisiona si el plan tiene voz y `not tenant.retell_agent_id` → 1 agente por negocio, editable (las "7 Marías" eran de pruebas). `/tenants/me` ahora trae `features[]`/`message_limit`/`call_limit`. Frontend: `hooks/useTenant.ts`, Sidebar filtra por módulo, landing/Register/Admin/Términos con 4 planes y precios nuevos. **"Pasar con el dueño"**: `AgentConfig.owner_contacts`+`owner_handoff_message` (migración `008_owner_handoff`), paso 6.8 en `webhook_handler` (si el número está en la lista → mensaje fijo + escala + avisa al dueño, 0 tokens), helper `phone_matches_any`, editable en `AgentConfigPage`. Precios viejos corregidos en `culqi_service.py`, `PRICING.md`, `docs/01`, `docs/11`, `MANUAL_DE_VENTAS.md`, `PLAN_COBRO_MANUAL.md`. **543 tests backend ✅ + `npm run build` ✅.** Pendiente del dueño al desplegar: `alembic upgrade head` (migraciones 007/008) + recrear contenedores (`docker compose up -d --build`) para tomar el `.env` y el código nuevos.

15. **Logo SVG propio + demo en celular (chat y llamada) + tema por cuenta + docs INDECOPI (2026-06-03):** **Logo rediseñado** como vector `frontend/public/logo.svg` (bot azul con corona dorada y gemas) — reemplaza al PNG; `Logo.tsx` y el favicon apuntan al SVG. **Demo de la landing rehecha como un CELULAR realista** (`PhoneDemo`): marco de teléfono con notch y barra de estado que **alterna entre el chat de WhatsApp y una llamada de voz simulada** (avatar con anillos pulsantes, cronómetro, onda de voz, botones de llamada). **Footer** con autoría: "Hecho con 💚 por Italo Eduardo Reyes Cordero" + "Todos los derechos reservados (D. Leg. N.º 822)". **Color de marca AHORA POR CUENTA (bug arreglado):** antes el color se guardaba global en la máquina y se "pegaba" entre la cuenta del negocio y la de superadmin; ahora `theme.store.ts` guarda las preferencias por usuario (`byUser`) y `App.tsx` carga las del usuario logueado al iniciar/cerrar sesión. **Documentos para registrar el software (INDECOPI)** en `docs/`: `Memoria_Descriptiva_AgentePro.docx`, `Manual_de_Usuario_AgentePro.docx` (generados con `docs/_gen_docx.py`) y `Codigo_Fuente_AgentePro.zip` (código fuente sin secretos). Falta solo completar DNI/domicilio/teléfono del autor en la memoria. `npm run build` ✅, todo verificado por screenshot. **Precios: ver punto 16 (el dueño pasó a 4 planes S/149/249/449/799).**

14. **Marca propia + landing premium + panel pulido (2026-06-03 — UI Fases 2-4):** **Logo oficial** integrado en TODA la app vía nuevo componente reutilizable `components/ui/Logo.tsx` (props `size`/`showText`): sidebar, login, registro, onboarding (bienvenida), landing (nav+footer+header del demo) y páginas legales. Favicon del navegador también usa el logo (`index.html`). **Landing premium** reescrita (`pages/landing/LandingPage.tsx`): nav sticky con blur, hero con título en degradado + demo animada, barra de badges de confianza, fila de stats (24/7 / <3s / +40% / 14 días), features con hover, sección "Listo en 3 pasos", testimonios, pricing con plan destacado elevado y CTA final en degradado. **Panel pulido:** saludo del dashboard como banner con degradado primary→secondary; KPIs con fondo de ícono a juego por color (mensajes/leads/llamadas/calientes) y sombra al hover. `npm run build` ✅ y verificado por screenshot headless. (Pendiente menor: las páginas legales tendrán URL pública al desplegar el dominio.)

13. **Recuperación de contraseña + errores de login bonitos (2026-06-01):** login devuelve mensajes en español ("Correo o contraseña incorrectos"). Para DUEÑOS (no superadmin): enlace "¿Olvidaste tu contraseña?" en login → `/forgot-password` → `POST /auth/password-reset-request` (no revela si el correo existe; crea solicitud pendiente). El super admin ve "Solicitudes de recuperación" en su panel, verifica identidad y pulsa **Restablecer** → se genera una contraseña al azar y se muestra **una sola vez** (modal con Copiar); también hay reset directo por negocio. El super admin NO se recupera por este flujo. Backend: modelo `PasswordResetRequest` + migración `003_password_reset`, endpoints en `admin.py`, `generate_temp_password()` en `core/security.py`. 92 rutas. Verificado de extremo a extremo. **OJO: la clave de super admin en LOCAL es `SuperAdmin2026`; la fuerte de `.env.production` solo aplica al desplegar.**

12. **UI premium / temas (2026-06-01):** paleta migrada a **variables CSS** (`index.css`: `:root` oscuro + `:root.light` claro) → **modo claro/oscuro** (toggle sol/luna en TopBar) y **color de marca por cliente** (Configuración → Apariencia: presets + color personalizado, se aplica al instante y persiste). **Fondo animado premium** (`AnimatedBackground`, auroras con framer-motion) global en TODAS las pantallas. **Animaciones** (framer-motion 12.40): transiciones entre páginas, entrada del dashboard, toasts y empty-states animados. **Skeletons** de carga (`Skeleton.tsx`) en KPIs. **Onboarding** con stepper numerado (checks + tooltips). Gráficos siguen el color de marca/tema. `npm run build` ✅. Detalle técnico en la memoria del proyecto.

11. **Copia OFF-SITE a Supabase Storage (2026-06-01):** cada backup se sube además a Supabase con `scripts/upload_supabase.sh` (lo llama `backup_db.sh` tras un dump OK; si falla la subida NO se pierde el backup local). `backup_loop.sh` instala `curl` (`apk add`) si hay credenciales. Recuperación con `scripts/download_supabase.sh list|<archivo>`. Vars (en `agentepro/.env` para dev, `backend/.env` para prod): `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (service_role), `SUPABASE_BACKUP_BUCKET` (def `db-backups`, **bucket privado**), `SUPABASE_BACKUP_PREFIX` (def `agentepro`), `SUPABASE_BACKUP_KEEP` (def 30). **Degrada solo** si faltan las vars. **Implementado y probado** (sintaxis `sh -n` OK, LF, rutas de degradación y error de red verificadas); para una subida REAL el dueño debe crear el bucket y poner la `service_role` key. Doc: `scripts/README.md`.

> ⚠️ **Riesgos restantes (conscientes):** (1) **RLS NATIVO de Postgres** (rol de BD restringido) — capa extra sobre el RLS de aplicación; se activa en producción. (2) ✅ **Backups off-site** — RESUELTO: subida automática a Supabase Storage (`scripts/upload_supabase.sh`); solo falta que el dueño cree el bucket y ponga la `service_role` key. (3) **Escala/sharding** — no es bug; aguanta cientos de clientes. Ver §9 (Auditoría) y `docs/PLAN_MAESTRO.md`.

---

## 4b. Auditoría de riesgos y calidad (2026-06-01)

Revisión enfocada (estilo SonarQube/seguridad) del backend. **No se ejecutó SonarQube real** (no instalado), pero se revisó el código a mano. Resultado: base sólida, sin agujeros críticos. Hallazgos:

**✅ Bien (sin acción):**
- **Sin inyección SQL:** todo usa SQLAlchemy ORM con parámetros; el único `text()` es `SELECT 1` (healthcheck).
- **Firmas de webhooks (Meta/Retell) con `hmac.compare_digest`** (comparación timing-safe) y se rechazan en producción si falta el secreto.
- **Aislamiento multi-tenant** cubre los **13 modelos con `tenant_id`** (lista `TENANT_MODELS` == modelos con la columna).

**🟡 Para producción (no bloquean dev, ya en el checklist de deploy):**
- ✅ **Secretos de producción listos (2026-06-01):** creado `backend/.env.production` (gitignored) con `SECRET_KEY`, `ADMIN_SECRET_KEY`, `META_VERIFY_TOKEN_SECRET` generados fuertes (`crypto.randomBytes`) + `SUPERADMIN_PASSWORD` nuevo, `ENVIRONMENT=production`, `DEBUG=false`, `ALLOW_FREE_SIGNUP=false` y placeholders `<<< ... >>>` para BD/Redis/dominio/keys. En deploy: copiar a `backend/.env`, rellenar placeholders. El `backend/.env` de dev sigue con secretos de dev (no se tocó). (Los defaults siguen en `config.py`; mejora opcional: forzar que vengan del entorno.)
- **`SECRET_KEY` deriva la clave de cifrado** de los tokens (WhatsApp/IG) en `utils/encryption.py`. **Rotar `SECRET_KEY` deja ilegibles los tokens guardados.** Documentarlo antes de rotar.
- **RLS nativo de Postgres** pendiente (capa extra, §9 riesgos).

**🟢 Menores (code smells):**
- **`CallSummary` no tiene `tenant_id`** → no entra en el filtro automático. **Hoy NO hay fuga:** los 2 accesos van vía `call_id` de una llamada ya filtrada por tenant, o con `join` explícito a `Call.tenant_id`. Riesgo solo teórico si un endpoint futuro hace `db.get(CallSummary, id)` directo. Recomendación: o se le añade `tenant_id` (migración) o se mantiene la regla "siempre acceder vía `Call`".
- **8 `except Exception:`** amplios (p. ej. `decrypt_if_value` devuelve el valor sin descifrar como fallback). Intencionales, pero SonarQube los marca; conviene acotar el tipo de excepción o loggear.

---

## 5. Qué se ha intentado (verificación)

- Levantar el stack localmente para verificación e2e: backend con `uvicorn` sobre **SQLite** (`smoke.db`) + frontend con `vite dev` + **Playwright/Chromium** manejando el navegador headless.
- Se creó la tabla de la BD con `Base.metadata.create_all` (las tablas no se crean en el lifespan).
- Se sembró/creó un superadmin de prueba para validar el panel.
- Se recorrió el flujo completo y se capturaron screenshots como evidencia (luego borrados).
- **Resultado: PASS.** Todas las entregas funcionan en runtime, no solo compilan.

---

## 6. Todo lo que falló (y cómo se resolvió)

| Problema | Causa | Estado |
|---|---|---|
| React crashea al registrar | FastAPI 422 devuelve `detail` como array; se renderizaba como hijo de React | ✅ **Arreglado** con `apiErrorMessage()` |
| Hashing de contraseñas roto ("password cannot be longer than 72 bytes" incluso con pw corta) | El Python global local tenía **bcrypt 5.0.0**, incompatible con passlib 1.7.4. El código fija `bcrypt==4.0.1` (Docker está bien) | ✅ Resuelto instalando bcrypt 4.0.1 localmente. **Docker no se ve afectado** |
| Register/login daban 422 con email `@…​.local` | `email-validator` (EmailStr) rechaza dominios reservados (`.local`) | ⚠️ No es bug; usar dominios reales (`@example.com`) al probar |
| El login del superadmin daba 401 en el navegador pero 200 por curl | El proxy de Vite (`localhost:8000`) resolvía a **IPv6 (::1)** y pegaba al **backend de Docker** (otra BD), no al backend local de prueba | ✅ Resuelto usando puerto dedicado + `VITE_PROXY_TARGET=http://127.0.0.1:<puerto>` |
| **Docker Desktop dejó de reenviar puertos (8000/5173)** | Durante la depuración se mató `com.docker.backend.exe` y `wslrelay.exe` (procesos de port-forwarding de Docker Desktop) | ✅ **Resuelto reiniciando Docker Desktop.** Engine OK, contenedores de `agentepro` arriba |

> ⚠️ **IMPORTANTE — nada se borró.** Solo se mataron procesos. **No** se ejecutó `docker rm`, `docker volume rm`, ni se borraron archivos de proyectos. Todos los contenedores (agentepro, phishguard-edu, alertavecinal, negocio_saas), imágenes y volúmenes siguen intactos. Los proyectos `phishguard-edu` y `alertavecinal` ya estaban apagados (Exited hace ~20h) **desde antes** de esta sesión.

---

## 7. Qué se planea hacer después

> Plan completo y por fases en **`docs/PLAN_MAESTRO.md`**. Resumen:

**Fase 0 — pulido sin keys (lo siguiente):**
1. Mejoras de UX fáciles: indicador de estado de WhatsApp en el dashboard, checklist de activación, estados vacíos amables, y poner el contacto real en `/app/upgrade` (hoy `wa.me/51999999999`).
2. (Opcional) code-splitting del bundle (~930 kB en un solo chunk).

**Fase 1 — encender IA:** poner `ANTHROPIC_API_KEY` y probar el agente en vivo.

**Fase 2 — vender WhatsApp:** desplegar con dominio público HTTPS + `META_APP_SECRET` + endurecer `.env`.

**Fase 3 — cobro:** cablear Culqi (`/signup` + widget), `ALLOW_FREE_SIGNUP=false`, pantalla billing/upgrade self-service.

**Fase 4 — add-ons:** voz (Twilio+Retell), Instagram (fal.ai), audios (OpenAI), CRM (HubSpot), emails (Resend).

**Fase 5 — robustez:** ✅ backups de Postgres (hechos), ✅ aislamiento por tenant (RLS de aplicación hecho); falta **RLS nativo de Postgres**, **backups off-site** y **monitoreo**.

> **Voz (aclaración):** cada negocio tiene su PROPIO agente Retell + número Twilio (creados al provisionar). Retell es cloud: atiende llamadas simultáneas sin interferencia; el límite es la concurrencia de tu plan Retell/Twilio. Detalle en `docs/PLAN_MAESTRO.md` §B.

---

## Cómo levantar todo (recordatorio)

```bash
# Opción A — Docker (lo que el usuario usa normalmente):
cd "D:/ESCRITORIO/PERSONAL/Proyecto AgentePro 2.0/agentepro"
docker compose up -d        # frontend :5173, backend :8000, postgres :5432, redis :6379

# Opción B — local sin Docker (para depurar):
# Backend (Python global, requiere uvicorn + bcrypt==4.0.1):
cd agentepro/backend
# (con Postgres real, o SQLite para smoke: DATABASE_URL="sqlite+aiosqlite:///./dev.db")
python -m uvicorn app.main:socket_app --host 127.0.0.1 --port 8000
# Frontend:
cd agentepro/frontend
npm install --legacy-peer-deps   # React 19 tiene conflictos de peer deps
npm run dev

# Verificar build del frontend:
npm run build   # tsc estricto + vite

# Superadmin: se auto-crea al arrancar el backend (app/core/seed.py) con
# las credenciales de agentepro/backend/.env (SUPERADMIN_EMAIL / SUPERADMIN_PASSWORD).
```
