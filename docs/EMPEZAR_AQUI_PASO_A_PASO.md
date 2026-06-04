# 🚀 EMPIEZA AQUÍ — Guía para poner AgentePro en producción (paso a paso, sin tecnicismos)

> Hecho para que NO te pierdas. Léelo de arriba hacia abajo, en orden. No saltes pasos.
> Si algo no entiendes, me mandas captura y te ayudo. Respira: es más fácil de lo que parece. 🙂

---

## 🧠 Parte 0 — Entiende el panorama (2 minutos)

AgentePro es un **robot (Claude) que atiende a tus clientes** por WhatsApp y por llamadas,
las 24 horas. Para funcionar, necesita "llaves" (las famosas *API keys*) de otros servicios.
Piensa en cada llave como **enchufar un electrodoméstico**: cada uno hace una cosa.

**La regla de oro:** no necesitas TODAS las llaves para arrancar. Necesitas **3 cosas mínimas**:

| # | Llave | ¿Para qué sirve? | ¿Obligatoria? |
|---|---|---|---|
| 1 | **Anthropic (Claude)** | El cerebro: redacta las respuestas | ✅ SÍ |
| 2 | **WhatsApp (Meta)** | El canal por donde escriben tus clientes | ✅ SÍ (si quieres WhatsApp) |
| 3 | **Servidor (Railway) + dominio** | Donde "vive" la app en internet | ✅ SÍ |

Todo lo demás (llamadas, Instagram, correos, backups, CRM) es **opcional** y lo agregas
después. **No te estreses por ellas ahora.**

---

## ✅ Parte 1 — El cerebro: Anthropic (Claude)  *(OBLIGATORIO)*

**¿Para qué sirve?** Es la inteligencia que entiende al cliente y escribe la respuesta.
Sin esto, el robot no piensa.

**Estado:** ya pusiste la llave. Solo falta **cargar saldo** (es pago por uso, centavos por chat).

**Pasos:**
1. Entra a **console.anthropic.com** e inicia sesión.
2. Arriba/abajo busca **"Plans & Billing"** (Planes y facturación).
3. **Add payment method** → agrega tu tarjeta.
4. **Buy credits** → compra **US$10** (te alcanza para muchísimas pruebas).
5. Listo. No tienes que copiar nada más; la llave ya está puesta.

---

## ✅ Parte 2 — WhatsApp con Meta  *(OBLIGATORIO si quieres WhatsApp)*

### 👉 La verdad honesta primero
- **WhatsApp es de Meta (Facebook).** No existe forma OFICIAL de usar WhatsApp para negocios
  sin una app de Meta. Así que sí, **es necesaria** para el WhatsApp oficial.
- El "pata" que viste conectó su número con un **método NO oficial** (escaneando un QR, como
  WhatsApp Web). Es más fácil, **pero va contra las reglas de WhatsApp y pueden BANEARLE el
  número** en cualquier momento. No te lo recomiendo para un negocio que cobras.
- **La buena noticia:** para PROBAR no necesitas tu número ni pelear con códigos. Meta te
  regala un **número de prueba**. Usa ese primero.

### 🐣 Lo más fácil: usar el NÚMERO DE PRUEBA de Meta (sin verificación, sin spam)
1. Entra a **developers.facebook.com** → inicia sesión con tu Facebook.
2. Arriba a la derecha: **My Apps → Create App**.
3. Tipo de app: elige **"Business"** → siguiente.
4. Ponle un nombre (ej. *AgentePro*) y crea la app.
5. En el tablero de la app, busca el producto **"WhatsApp"** → botón **"Set up"**.
6. Te llevará a **"API Setup"**. Ahí verás:
   - **"From" (número de prueba):** Meta te da uno gratis. **Ese lo usas, NO tu número.**
   - **"To":** agrega **tu celular** como destinatario de prueba (te llega un código por
     WhatsApp para confirmarlo — esto es normal y es solo para TU número de prueba).
   - **Phone number ID** y un **Temporary access token**: estos dos los vas a copiar.
7. Esos datos (**Phone number ID** y **token**) se ponen DENTRO de AgentePro, en el panel del
   negocio (sección **"Conectar WhatsApp"**), NO en el archivo de configuración.

### 🔑 Lo que SÍ va en la configuración del servidor (en Railway):
En el tablero de la app de Meta → **Settings → Basic**, copia:
- **App ID** → variable `META_APP_ID`
- **App Secret** (botón "Show") → variable `META_APP_SECRET`

**¿Para qué sirven estas dos?** Para que AgentePro confirme que los mensajes vienen de verdad
de WhatsApp y no de un impostor (seguridad). Se ponen **una sola vez**.

### 😵 ¿Te bloqueó por spam con los códigos?
Pasó porque intentaste registrar **tu propio número** como remitente. Solución:
- **Espera 24 horas** (el bloqueo es temporal).
- **No registres tu número todavía.** Usa el **número de prueba** de Meta (paso de arriba).
- Tu número real lo registras MÁS ADELANTE, cuando ya vayas a vender (eso requiere
  "verificación del negocio" en Meta, que es un trámite aparte de unos días).

> **Resumen Parte 2:** Para probar → usa el número de prueba de Meta (fácil). Copia `META_APP_ID`
> y `META_APP_SECRET`. Tu número real y la verificación de negocio quedan para después.

---

## 📞 Parte 3 — Llamadas con IA: Twilio + Retell  *(OPCIONAL)*

**¿Para qué sirve cada uno?**
- **Twilio** = te da el **número de teléfono** (el negocio recibe/hace llamadas desde ahí).
- **Retell** = es la **voz con IA** que habla en la llamada (contesta como persona).

**Estado:** ya pusiste las dos llaves. Solo falta confirmar que tengan **saldo**.

**Pasos Twilio:**
1. Entra a **twilio.com** → tu consola.
2. Agrega saldo (**Billing → Add funds**, US$20 está bien para empezar).
3. AgentePro compra el número solo cuando das de alta un negocio. No tienes que comprarlo a mano.

**Pasos Retell:**
1. Entra a **retellai.com** → tu cuenta.
2. Revisa que tu plan/saldo esté activo (cobran por minuto de llamada).
3. La llave `RETELL_API_KEY` ya la tienes puesta.

> Si por ahora solo quieres probar **WhatsApp**, puedes **saltarte esta parte** y volver después.

---

## 🎁 Parte 4 — Extras opcionales (puedes ignorarlos al inicio)

| Llave | ¿Para qué sirve? | ¿La necesitas ya? |
|---|---|---|
| **FAL** (`FAL_KEY`) | Generar imágenes con IA para posts de Instagram | No |
| **Resend** (`RESEND_API_KEY`) | Enviar correos (avisos, bienvenida) | No |
| **Supabase** | Guardar copias de seguridad e imágenes | No |
| **Instagram** (`META_INSTAGRAM_*`) | Atender DMs de Instagram | No |

**Nota Resend:** te lo dejé configurado con `onboarding@resend.dev` (remitente de prueba).
Por ahora solo te llegarán correos a TU correo. Cuando estés en vivo, verificas tu dominio
`tuagentepro.xyz` en Resend para enviar a clientes.

**Nota Supabase (CORRIGE ESTO si lo vas a usar):** pegaste una **clave** donde va la **URL**.
Lo correcto (en Supabase → Project Settings → API):
- `SUPABASE_URL` = `https://TUPROYECTO.supabase.co`  ← la dirección web, NO una clave
- `SUPABASE_KEY` = la *anon / publishable key*
- `SUPABASE_SERVICE_KEY` = la *service_role key* (esta te falta)
> Si no lo usas todavía, **déjalo vacío** y listo. No pasa nada.

---

## 🚫 Parte 5 — Lo que NO necesitas (ignóralas, ahorra tiempo y dinero)

- **OpenAI** ❌ — era para transcribir audios; ya hicimos que el robot pida que le escriban.
- **Modal** ❌ (por ahora) — sirve para automatizaciones avanzadas (campañas, reportes). El
  servidor ya trae un "worker" que cubre lo básico. Modal lo agregas mucho después, si crece.
- **Culqi** ❌ — no usas pasarela de pago; cobras por **Yape**.
- **HubSpot** ❌ — no lo necesitas: AgentePro **ya tiene su propio CRM** (tus contactos, leads
  y conversaciones se ven en el panel). Lo que te pidieron en HubSpot (link del sitio) era
  `https://tuagentepro.xyz`, pero mejor **ni lo configures**.

---

## 🗂️ Parte 6 — El CRM y "lo que ofrece tu negocio" (lo de Notion)

**Tu duda:** querías Notion como base de datos para que el robot sepa lo que ofrece el negocio.

**La verdad tranquilizadora:** **no necesitas Notion para salir a producción.** Hoy, "lo que
ofrece tu negocio" se configura **dentro del panel de AgentePro**, en la sección **"Agente IA"**:
ahí pones tus **servicios, precios, horarios y preguntas frecuentes**, y el robot responde con eso.
Y los **contactos/clientes** se guardan solos en la sección **"Contactos"** (ese es tu CRM, ya incluido).

**Sobre conectar Notion:** sí se puede construir (que el robot lea de tu Notion), pero es una
**función nueva que hay que programar**. Te recomiendo de corazón: **primero sal a producción**
con lo que ya funciona, y **apenas estés en vivo, te armo la conexión con Notion**. Así no
sumamos más pasos ahora que ya tienes bastante. (Cuando quieras, me dices "hagamos lo de Notion"
y lo construyo.)

---

## 🌐 Parte 7 — Subir todo a internet (Railway + tu dominio)

**¿Para qué?** Para que AgentePro deje de vivir solo en tu compu y esté en `tuagentepro.xyz`.

**Lo que necesitas tener a la mano:**
- Tu dominio **tuagentepro.xyz** (ya lo tienes ✅).
- Una cuenta de **GitHub** (gratis) y una de **Railway** (gratis para empezar).

**Pasos (resumen — el detalle completo está en `GUIA_DESPLIEGUE_RAILWAY.md`):**
1. Subes el proyecto a **GitHub** (yo te ayudo con los comandos cuando llegues aquí).
2. En **Railway**: *New Project → Deploy from GitHub repo* → eliges tu repo.
3. Agregas **PostgreSQL** y **Redis** (dos botones).
4. En el servicio web: *Root Directory* = `agentepro`, *Dockerfile* = `Dockerfile.railway`.
5. Pegas las **variables** (todas tus llaves + `FRONTEND_URL=https://tuagentepro.xyz`).
6. Conectas el **dominio** (un registro CNAME; te guío en el momento).
7. Railway le pone el **candado HTTPS** solo. Listo: `https://tuagentepro.xyz` abre tu app.

> Cuando llegues a esta parte, **hazlo conmigo paso a paso**; es donde más te puedo ayudar en vivo.

---

## ✅ Parte 8 — Checklist final para estar EN PRODUCCIÓN

Marca cada uno cuando lo tengas:

**Mínimo para vender por WhatsApp:**
- [ ] 1. Anthropic con **saldo** cargado.
- [ ] 2. App de Meta creada → `META_APP_ID` y `META_APP_SECRET` copiados.
- [ ] 3. Número de **prueba** de Meta funcionando + tu celular agregado como destinatario.
- [ ] 4. Proyecto subido a **GitHub**.
- [ ] 5. Desplegado en **Railway** (web + Postgres + Redis).
- [ ] 6. Dominio **tuagentepro.xyz** conectado y abriendo la app.
- [ ] 7. Páginas legales visibles: `tuagentepro.xyz/privacidad` y `/terminos` (Meta las exige).

**Cuando quieras llamadas (opcional):**
- [ ] 8. **Twilio** con saldo.
- [ ] 9. **Retell** con plan/saldo activo.

**Para vender a clientes reales por WhatsApp (más adelante):**
- [ ] 10. **Verificación de negocio** en Meta + registrar tu número real.

---

## 🧪 Cómo haremos la PRUEBA real (cuando tengas 1–6 listo)
1. Creamos un **negocio de prueba** en tu panel de Super Admin.
2. Conectamos el **número de prueba** de Meta.
3. Configuramos en "Agente IA" lo que ofrece ese negocio (servicios, precios, horarios).
4. Le escribes desde **tu celular** y el robot te responde. 🎉
5. (Opcional) Probamos una **llamada** con Twilio+Retell.

---

## 🆘 Si te sientes perdido
No intentes hacer todo de golpe. **Haz solo la Parte 1 y la Parte 2.** Cuando las tengas,
me avisas y seguimos con el despliegue juntos. Vamos de a poco. 💪

*(Las llaves que ya tienes puestas: Anthropic, Twilio, Retell, FAL, Resend. Te faltan
principalmente las de **Meta/WhatsApp**. Lo demás es opcional.)*
