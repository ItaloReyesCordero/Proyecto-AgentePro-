# Guía de despliegue de AgentePro en Railway

> Dominio: **tuagentepro.xyz** · Arquitectura: **un solo servicio web** (el backend
> sirve también el frontend, mismo origen) + **Postgres** + **Redis** + **worker**.

Esta guía te lleva de cero a la app funcionando en `https://tuagentepro.xyz`.

---

## 0. Lo que ya dejé listo (no tienes que tocar código)
- `agentepro/Dockerfile.railway` → imagen **todo en uno**: compila el frontend y lo
  sirve desde el backend (FastAPI). Así no hay problemas de CORS ni de URLs.
- El backend ahora **acepta la `DATABASE_URL` tal cual la da Railway** (la convierte
  sola a async/sync). Solo defines `DATABASE_URL` y funciona.
- El backend sirve el frontend desde `/app/frontend_dist` automáticamente.

---

## 1. Sube el proyecto a GitHub (una vez)
Railway despliega desde un repositorio de GitHub.
1. Crea un repositorio **privado** en GitHub (ej. `agentepro`).
2. Sube la carpeta del proyecto. Si no usas Git aún, instálalo y desde la carpeta
   raíz del proyecto:
   ```
   git init
   git add .
   git commit -m "AgentePro"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/agentepro.git
   git push -u origin main
   ```
   > El `.gitignore` ya evita subir secretos (`.env`), `node_modules` y backups.
   > **Importante:** como `backend/.env` está ignorado, las claves se ponen en
   > Railway (paso 5), NO en el repo.

---

## 2. Crea el proyecto en Railway
1. Entra a **railway.app** e inicia sesión con GitHub.
2. **New Project → Deploy from GitHub repo →** elige tu repo `agentepro`.
3. Railway creará un primer servicio. Lo configuramos en el paso 4.

---

## 3. Agrega la base de datos y Redis (servicios administrados)
En el mismo proyecto:
1. **New → Database → Add PostgreSQL.**
2. **New → Database → Add Redis.**

Railway los crea y expone sus variables automáticamente (las usaremos en el paso 5).

---

## 4. Configura el servicio WEB (el backend que sirve todo)
Abre el servicio que se creó desde tu repo → pestaña **Settings**:
- **Root Directory:** `agentepro`
- **Build → Dockerfile Path:** `Dockerfile.railway`
- **Networking → Generate Domain** (te da una URL temporal `*.up.railway.app`;
  el dominio propio lo conectamos en el paso 7).

> Railway detecta el `Dockerfile.railway` y construye la imagen todo-en-uno.

---

## 5. Variables de entorno del servicio web
En el servicio web → pestaña **Variables**, agrega estas. Las de la base de datos y
Redis se **referencian** a los servicios que creaste (Railway autocompleta con
`${{...}}`):

**Base de datos y cache (referencias):**
```
DATABASE_URL = ${{Postgres.DATABASE_URL}}
REDIS_URL    = ${{Redis.REDIS_URL}}
```

**Básicas:**
```
ENVIRONMENT      = production
DEBUG            = false
FRONTEND_URL     = https://tuagentepro.xyz
ALLOW_FREE_SIGNUP = false
SECRET_KEY       = (genera uno largo aleatorio)
ADMIN_SECRET_KEY = (genera otro)
SUPERADMIN_EMAIL    = tu-correo-admin@tudominio.com
SUPERADMIN_PASSWORD = (una contraseña fuerte para tu cuenta de super admin)
SUPERADMIN_NAME     = Italo Reyes
```
> Para generar claves aleatorias: en cualquier terminal
> `python -c "import secrets; print(secrets.token_hex(32))"`.

**IA (ya la tienes):**
```
ANTHROPIC_API_KEY = sk-ant-...   (y carga saldo en console.anthropic.com)
```

**Las demás claves que ya conseguiste** (cópialas igual que en tu `.env`):
`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `RETELL_API_KEY`, `FAL_KEY`,
`RESEND_API_KEY`, `RESEND_FROM_EMAIL`, y cuando las tengas:
`META_APP_ID`, `META_APP_SECRET`, `HUBSPOT_ACCESS_TOKEN`, `HUBSPOT_PORTAL_ID`,
`SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`.

**Datos de cobro (Yape) — para la pantalla de pago:**
```
PAYMENT_YAPE_NUMBER     = 916085873
PAYMENT_ACCOUNT_HOLDER  = Italo Eduardo Reyes Cordero
PAYMENT_CONTACT_WHATSAPP = 51916085873
```

> No necesitas `OPENAI_API_KEY` ni `MODAL_*` (no transcribimos audios).
> No necesitas `CULQI_*` (cobras por Yape).

Al guardar, el servicio se **redeploya**. En el primer arranque corre las
migraciones (`alembic upgrade head`) y siembra tu cuenta de super admin.

---

## 6. (Recomendado) Servicio WORKER para tareas en segundo plano
Las automatizaciones, llamadas salientes y posts de Instagram usan un worker.
1. **New → Empty Service** (o "Deploy from repo" del mismo repo).
2. Settings → **Root Directory** `agentepro`, **Dockerfile Path** `Dockerfile.railway`.
3. Settings → **Deploy → Start Command:**
   ```
   celery -A app.workers.celery_app worker --loglevel=info
   ```
4. Variables: las MISMAS que el web (puedes usar **Shared Variables** del proyecto
   para no repetirlas). El worker **no** necesita dominio.

> Si por ahora solo quieres WhatsApp básico, puedes omitir el worker y agregarlo
> después; el chat responde sin él.

---

## 7. Conecta tu dominio tuagentepro.xyz
1. En el **servicio web** → **Settings → Networking → Custom Domain →** escribe
   `tuagentepro.xyz` (y opcionalmente `www.tuagentepro.xyz`).
2. Railway te dará un destino **CNAME** (algo como `xxxx.up.railway.app`).
3. En tu proveedor del dominio (donde compraste `tuagentepro.xyz`), en la zona DNS:
   - Crea un registro **CNAME** del host `@` (o `www`) apuntando a ese destino.
   - Si tu proveedor no permite CNAME en la raíz (`@`), usa el registro **A/ALIAS**
     que Railway indique, o pon el dominio en **Cloudflare** (gratis) y desde ahí
     haces el CNAME a Railway. Cloudflare sirve perfecto para el DNS.
4. Espera a que propague (minutos). Railway emite el certificado HTTPS solo.

Cuando termine, `https://tuagentepro.xyz` abre tu app. 🎉

---

## 8. Verificación
- Abre `https://tuagentepro.xyz` → debe cargar la landing con el logo.
- `https://tuagentepro.xyz/health` → `{"status":"healthy"}`.
- Entra con tu cuenta de super admin (la del paso 5) en `/login`.

---

## 9. Costos aproximados en Railway
- Plan Hobby ~US$5/mes de crédito incluido + uso.
- Web + Postgres + Redis + worker corriendo siempre puede ir ~US$10–20/mes según
  tráfico. Puedes empezar **sin worker** para gastar menos.

---

## 10. Actualizaciones futuras
Cada vez que hagas `git push` a `main`, Railway **redeploya solo**. Las migraciones
de base de datos corren automáticamente en cada arranque.

---

## Notas
- Si prefieres no usar GitHub, puedes usar la **CLI de Railway** (`railway up`) desde
  la carpeta `agentepro/`, pero GitHub es lo más cómodo para redeploys.
- El despliegue en **un solo VPS** (Caddy) sigue disponible con
  `docker-compose.deploy.yml` (ver `GUIA_DESPLIEGUE_PASO_A_PASO.md`) por si algún día
  lo prefieres.
