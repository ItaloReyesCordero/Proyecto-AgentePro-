# 🧪 Prueba de WhatsApp en LOCAL (con túnel) — datos y pasos

> Archivo temporal de la prueba del 2026-06-03. La URL del túnel y el token de Meta
> son TEMPORALES (ver avisos abajo).

## ⭐ RECOMENDADO: probar por TWILIO (sin Meta, sin bloqueos)

AgentePro ahora también se conecta por **Twilio WhatsApp**. El **Sandbox de Twilio**
funciona al instante, sin pelear con Meta. Ya está probado en el código (el robot
respondió). Pasos:

1. **Twilio Console** → menú **Messaging → Try it out → Send a WhatsApp message**.
2. Verás el **número del Sandbox** (normalmente **+1 415 523 8886**) y un código tipo
   **`join algo-algo`**.
3. Desde **tu celular (WhatsApp)**, envía ese **`join algo-algo`** al número del Sandbox.
   (Eso conecta tu teléfono al Sandbox.)
4. En esa misma página de Twilio → **Sandbox settings / Configuración** → en el campo
   **"When a message comes in"** pega esta URL (método **POST**):
   ```
   https://settled-mailed-nissan-paper.trycloudflare.com/webhooks/twilio/whatsapp/barberia-don-pepe-af0a24
   ```
   y **guarda**.
5. Desde tu celular, escribe al número del Sandbox (ej. *"hola, cuánto cuesta el corte?"*).
   **El robot te responde.** 🎉
6. Míralo en vivo en **http://localhost:5173 → Conversaciones**.

> **Producción (después):** en Twilio pides un "WhatsApp Sender" con tu número real;
> Twilio se encarga del trámite con Meta por ti. Sin bloqueos de cuenta.
> Recuerda: el **túnel y el Docker** deben seguir encendidos durante la prueba.

---

## (Alternativa) Datos de tu prueba por META — solo si desbloqueas tu cuenta
- **Negocio:** Barbería Don Pepe
- **Slug:** `barberia-don-pepe-af0a24`
- **Número de prueba (Meta):** +1 (555) 652-2851
- **Phone Number ID:** 1117004381500028

## Lo que pones en Meta (webhook)
- **Callback URL (URL de devolución de llamada):**
  ```
  https://settled-mailed-nissan-paper.trycloudflare.com/webhooks/whatsapp/barberia-don-pepe-af0a24
  ```
- **Verify token (token de verificación):**
  ```
  8623a574ceef6f2eaa07eed944bf5d60
  ```
- **Campo a suscribir:** `messages`

## Pasos en Meta (developers.facebook.com → tu app → WhatsApp → Configuración)
1. En **"Configuración" / "Configuration"**, busca **"Webhook"** → **Editar**.
2. Pega la **Callback URL** y el **Verify token** de arriba → **Verificar y guardar**
   (debe aceptarlo; ya lo probamos y funciona).
3. En **"Webhook fields" / "Campos del webhook"** → **Administrar** → activa **`messages`**.

## Probar
1. Asegúrate de que tu **celular** esté agregado como destinatario de prueba en Meta
   (en la sección "API Setup", el campo **"To"**).
2. Desde tu celular, **envía un WhatsApp al número +1 (555) 652-2851** (ej. "hola, cuánto cuesta el corte?").
3. El robot debe responderte. 🎉
4. Míralo en vivo en el panel: **http://localhost:5173 → Conversaciones**.

## ⚠️ Avisos importantes
- Mantén **encendida la laptop, el Docker y el túnel** mientras pruebas. Si se apagan,
  deja de funcionar.
- La **URL del túnel** (`settled-mailed-...`) cambia si se reinicia cloudflared. Si la
  reinicias, hay que actualizar la Callback URL en Meta.
- El **token de Meta caduca en ~24 h** (es de prueba). Si deja de responder al día
  siguiente, genera un token nuevo en Meta y vuélvelo a conectar.
- Esto es solo para PROBAR. Para algo estable → desplegar en Railway (dominio fijo).
