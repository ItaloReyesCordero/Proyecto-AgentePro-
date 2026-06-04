# Cómo conseguir cada API key — paso a paso

> Guía para llenar `agentepro/backend/.env`. Verificado contra lo que el sistema
> realmente usa (`app/config.py`). Las pantallas de cada proveedor pueden cambiar
> un poco con el tiempo, pero el flujo es este.
>
> **Orden recomendado:** primero las de la sección 🟢 (gratis / imprescindibles),
> luego 🟡 cuando quieras vender, y 🔵 solo si las necesitas.

---

## Cómo se edita el .env

1. Abre `agentepro/backend/.env` con un editor de texto.
2. Cada línea es `NOMBRE=valor` (sin comillas, sin espacios alrededor del `=`).
3. Después de cambiarlo, reinicia el backend para que tome los valores:
   ```
   docker compose restart backend worker
   ```

---

# 🟢 Nivel 1 — Lo que NO cuesta y debes poner primero

Estas no son APIs externas; las generas o defines tú.

## 1. `SECRET_KEY` (firma de sesiones y cifrado)
1. Abre una terminal.
2. Ejecuta: `openssl rand -hex 32` (en Windows con Git Bash) **o** en Python:
   `python -c "import secrets; print(secrets.token_hex(32))"`.
3. Copia el texto largo que sale y pégalo: `SECRET_KEY=ese_texto`.
> ⚠️ En producción **cámbiala** por una nueva. Si la cambias, las sesiones activas se invalidan (los usuarios vuelven a iniciar sesión).

## 2. `ADMIN_SECRET_KEY` (llave maestra de administración por API)
1. Genera otra igual que la anterior (`openssl rand -hex 32`).
2. Pégala: `ADMIN_SECRET_KEY=otro_texto`.
> Sirve para llamar endpoints de administración por API sin tu sesión. Guárdala en privado.

## 3. `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD` / `SUPERADMIN_NAME` (tu cuenta de dueño)
1. Pon tu email real, una contraseña fuerte y tu nombre:
   ```
   SUPERADMIN_EMAIL=tucorreo@gmail.com
   SUPERADMIN_PASSWORD=UnaClaveFuerte2026
   SUPERADMIN_NAME=Tu Nombre
   ```
2. Se crea sola al arrancar el backend. (Si ya existe ese email, no la recrea.)

---

# 🟢 Nivel 2 — La ÚNICA de pago imprescindible

## 4. `ANTHROPIC_API_KEY` (el cerebro: Claude)
Sin esto, el agente **no responde de verdad**. Es lo primero que debes pagar.

1. Entra a **https://console.anthropic.com** y crea una cuenta.
2. Menú **Settings → Billing** → agrega un método de pago y carga saldo (puedes empezar con poco, p. ej. US$5–20).
3. Ve a **Settings → API Keys → Create Key**.
4. Ponle un nombre (ej. "AgentePro") y **copia la clave** (empieza con `sk-ant-...`). Solo se muestra una vez.
5. Pégala: `ANTHROPIC_API_KEY=sk-ant-...`.
6. (Opcional) Los modelos ya vienen configurados: `CLAUDE_MODEL_DEFAULT=claude-sonnet-4-6` (rápido/barato) y `CLAUDE_MODEL_COMPLEX=claude-opus-4-8` (tareas complejas). No necesitas tocarlos.

> 💡 Para probar: con esta key ya funciona el botón **"Probar agente"** en el dashboard (Agente IA), sin necesidad de WhatsApp.

---

# 🟡 Nivel 3 — Canal principal: WhatsApp (para vender de verdad)

> WhatsApp Business API tiene **dos partes**: lo que pones TÚ una vez (la app de Meta) y lo que pone **cada cliente** (su número y token). El sistema ya guarda lo del cliente cifrado.

## 5. `META_APP_SECRET` y `META_APP_ID` (tu app de Meta, una sola vez)
1. Entra a **https://developers.facebook.com** e inicia sesión con tu Facebook.
2. **My Apps → Create App → tipo "Business"**. Ponle nombre (ej. "AgentePro").
3. Dentro de la app, agrega el producto **WhatsApp** ("Set up").
4. En **App settings → Basic** copia:
   - **App ID** → `META_APP_ID=...`
   - **App Secret** (botón "Show") → `META_APP_SECRET=...`
5. `META_VERIFY_TOKEN_SECRET`: invéntate un texto secreto largo (ej. `openssl rand -hex 16`) → `META_VERIFY_TOKEN_SECRET=...`. El sistema lo usa para generar un token de verificación distinto por cada negocio.

## 6. Lo que pone CADA cliente (no va en .env)
Esto el cliente lo hace en su **onboarding** dentro del dashboard:
1. En la app de Meta del cliente (o la tuya en modo multi-cliente), sección **WhatsApp → API Setup**, obtiene su **Phone Number ID** y un **Access Token**.
2. Los pega en el paso "Conectar WhatsApp" del onboarding. El sistema los guarda **cifrados**.
3. El sistema le muestra su **Webhook URL** (`.../webhooks/whatsapp/su-slug`) y su **Verify Token**. El cliente los copia en **Meta → WhatsApp → Configuration → Webhook** y se suscribe al campo **messages**.

> ⚠️ El webhook necesita una **URL pública HTTPS** (no `localhost`). Por eso WhatsApp real solo funciona cuando despliegues a un servidor (ver plan maestro).

---

# 🔵 Nivel 4 — Llamadas de voz (opcional, cuando quieras ofrecerlo)

> Necesitas **dos** servicios juntos: Twilio (el número de teléfono) + Retell (la IA que habla). Ver la explicación de arquitectura en `PLAN_MAESTRO.md`.

## 7. `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_DEFAULT_PHONE_NUMBER`
1. Crea cuenta en **https://www.twilio.com** y verifica tu identidad.
2. En la **Console** (página principal), copia **Account SID** y **Auth Token** → pégalos.
3. Carga saldo (Billing). Para Perú, los números móviles tienen requisitos regulatorios; mientras tanto puedes usar un número de prueba o US.
4. (Opcional) Si quieres un número por defecto: cómpralo en **Phone Numbers → Buy a number** y ponlo en `TWILIO_DEFAULT_PHONE_NUMBER=+1...`.

## 8. `RETELL_API_KEY` (la voz IA)
1. Crea cuenta en **https://dashboard.retellai.com**.
2. Ve a **API Keys** y crea una. Cópiala → `RETELL_API_KEY=...`.
3. Agrega método de pago (cobran por minuto de llamada).
4. `RETELL_WEBHOOK_SECRET`: opcional, para validar los eventos que Retell te manda. Si Retell te da un secreto de webhook, pégalo; si no, déjalo vacío.
> El sistema crea el agente de voz de cada negocio **automáticamente** al darlo de alta. Solo necesitas esta key.

---

# 🔵 Nivel 5 — Add-ons opcionales

## 9. `OPENAI_API_KEY` (transcribir audios de WhatsApp con Whisper)
1. Entra a **https://platform.openai.com**, crea cuenta y carga saldo.
2. **API keys → Create new secret key** → cópiala (`sk-...`) → `OPENAI_API_KEY=sk-...`.
> Solo necesario si tus clientes reciben **notas de voz** por WhatsApp y quieres que el agente las entienda.

## 10. `FAL_KEY` (imágenes para Instagram)
1. Entra a **https://fal.ai**, crea cuenta.
2. En **Dashboard → API Keys / Keys**, crea una → `FAL_KEY=...`.
> Necesario para generar las **imágenes** de los posts de Instagram. El texto lo hace Claude.

## 11. `HUBSPOT_ACCESS_TOKEN` / `HUBSPOT_PORTAL_ID` (CRM)
1. Entra a **https://app.hubspot.com** (cuenta gratis sirve).
2. **Settings (⚙️) → Integrations → Private Apps → Create a private app**.
3. En **Scopes** marca: `crm.objects.contacts` (read/write), `crm.objects.deals` (read/write), y tasks/notes si quieres.
4. Crea la app y copia el **Access Token** (`pat-...`) → `HUBSPOT_ACCESS_TOKEN=pat-...`.
5. El **Portal ID** está arriba a la derecha en tu cuenta HubSpot → `HUBSPOT_PORTAL_ID=...`.

## 12. `RESEND_API_KEY` / `RESEND_FROM_EMAIL` (emails de bienvenida)
1. Entra a **https://resend.com**, crea cuenta.
2. **API Keys → Create API Key** → cópiala (`re_...`) → `RESEND_API_KEY=re_...`.
3. Para enviar desde tu dominio, agrégalo y verifícalo en **Domains** (registros DNS). Mientras tanto puedes usar el dominio de pruebas que te da Resend.
4. `RESEND_FROM_EMAIL=noreply@tudominio.com`.

## 13. `CULQI_PUBLIC_KEY` / `CULQI_SECRET_KEY` / `CULQI_WEBHOOK_SECRET` (cobros en Perú)
1. Crea cuenta en **https://culqi.com** y completa la verificación del negocio.
2. En el **panel → Desarrollo → API Keys** copia la **llave pública** (`pk_...`) y la **secreta** (`sk_...`).
   - Para pruebas usa las que dicen `test`; para cobrar de verdad las `live`.
3. Pega: `CULQI_PUBLIC_KEY=pk_...`, `CULQI_SECRET_KEY=sk_...`.
4. `CULQI_WEBHOOK_SECRET`: si configuras webhooks de Culqi, pega el secreto que te den.
> ⚠️ Mientras `CULQI_SECRET_KEY` esté vacío, el cobro es **simulado** y `ALLOW_FREE_SIGNUP=true` deja registrarse gratis. Para cobrar de verdad: pon la key y `ALLOW_FREE_SIGNUP=false`.

## 14. `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` (tareas programadas en la nube)
1. Crea cuenta en **https://modal.com**.
2. Instala y autentícate: `pip install modal` y luego `modal token new` (abre el navegador).
3. Copia el token ID y secret que genera → pégalos.
> Solo si quieres correr seguimientos/reportes/Instagram programados en la nube de Modal en vez de Celery.

## 15. `SUPABASE_URL` / `SUPABASE_KEY` (almacenamiento de archivos/media)
1. Crea proyecto en **https://supabase.com**.
2. **Project Settings → API**: copia el **Project URL** → `SUPABASE_URL=...` y la **anon/service key** → `SUPABASE_KEY=...`.
3. En **Storage** crea un bucket llamado como `SUPABASE_STORAGE_BUCKET` (por defecto `agentepro-media`).

---

## Resumen rápido de prioridad

| Para... | Pon estas keys |
|---|---|
| **Probar el sistema (UI + agente de prueba)** | Nivel 1 + `ANTHROPIC_API_KEY` |
| **Vender WhatsApp con IA** | + Nivel 3 (Meta) + desplegar con dominio público |
| **Agregar llamadas de voz** | + Twilio + Retell |
| **Agregar Instagram / audios / CRM / emails** | + fal.ai / OpenAI / HubSpot / Resend |
| **Cobrar automático** | + Culqi (y `ALLOW_FREE_SIGNUP=false`) |
