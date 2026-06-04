# 🏆 Guía TOTAL — Dejar tu negocio como ENTERPRISE y probar TODO

> Guía exhaustiva para **un solo negocio real** (el tuyo) en tu plataforma ya
> desplegada en **Railway**. Te lleva desde conectar tu dominio `tuagentepro.xyz`
> hasta tener WhatsApp + Llamadas de voz (María) + Automatizaciones funcionando, con
> el plan **Enterprise (S/ 799)** completo, y **cómo probar cada cosa**.
>
> Estado de partida (2026-06-04): plataforma viva en
> `https://proyecto-agentepro-production.up.railway.app/`. Falta: conectar dominio +
> dar de alta el negocio como Enterprise + número Twilio + voz Retell.

---

## 🧠 0. Cómo encaja TODO (léelo una vez, te ahorra horas)

Hay **3 servicios externos** que tu sistema usa. Tú tienes UNA cuenta de cada uno (sirve
para todos tus negocios):

| Servicio | Qué hace | Lo necesitas para |
|---|---|---|
| **Anthropic (Claude)** | El cerebro que escribe/decide | WhatsApp y voz |
| **Twilio** | Te da el NÚMERO de teléfono y recibe las llamadas/WhatsApp | WhatsApp y voz |
| **Retell** | La VOZ con IA (María) que habla en la llamada | solo voz |

### La cadena de una LLAMADA (lo más confuso, aquí claro):

```
Cliente marca el número Twilio del negocio
        │
        ▼
  TWILIO recibe la llamada y pregunta a tu backend:
  "¿qué hago con esta llamada?"  → POST https://tuagentepro.xyz/webhooks/twilio/voice/{slug}
        │
        ▼
  TU BACKEND responde con una instrucción (TwiML) que dice:
  "conecta el audio de esta llamada al agente de Retell {retell_agent_id}"
        │
        ▼
  El audio viaja por WebSocket a  wss://api.retellai.com/audio-websocket/{retell_agent_id}
        │
        ▼
  RETELL (María) escucha, piensa con Claude y RESPONDE por voz, en tiempo real
        │
        ▼
  Al colgar, Retell avisa a tu backend (webhook /webhooks/retell/{slug})
  y la llamada queda guardada en tu panel → Llamadas
```

**Punto clave:** el número de Twilio **NO se "mete" dentro de Retell**. Se conectan a
través de **tu backend**: Twilio pregunta → tu backend ordena "conéctate a Retell". Por
eso **el número y el agente de Retell se crean por separado, pero tu sistema los une
solo**. Tú no tienes que enlazarlos a mano.

### ¿El agente de Retell se crea a mano o automático?
**Automático, uno por negocio.** Cuando das de alta el negocio como **Enterprise** (o
Professional) desde tu **panel de Super Admin → Crear negocio**, tu sistema, en un solo
clic, hace TODO esto por dentro (lo vi en el código `tenant_provisioner.py`):

1. Crea el negocio (tenant) + el usuario dueño.
2. Crea la config del agente de chat "María" (con FAQs según el rubro).
3. Crea la config de voz.
4. **Compra un número en Twilio** y le configura el webhook de voz.
5. **Crea el agente de voz en Retell** (LLM + agente "María") y guarda su `retell_agent_id`.
6. Crea las **automatizaciones** del plan (Enterprise = seguimiento + reporte semanal +
   **reactivación de contactos**).

> ⚠️ **MUY IMPORTANTE:** esa magia automática **solo ocurre al CREAR el negocio**.
> Si ya tienes un negocio de prueba y solo le **cambias el plan** a Enterprise, **NO**
> se compra número ni se crea el agente de Retell. Por eso, para tu negocio real, lo
> más limpio es **borrar el de prueba y crearlo de nuevo como Enterprise** (Sección 5).

---

## 📋 Orden correcto (resumen de toda la guía)

1. **Conectar el dominio** `tuagentepro.xyz` a Railway. *(Sección 1)*
2. **Poner/verificar las variables** en Railway — sobre todo `FRONTEND_URL`. *(Sección 2)*
3. **Preparar Twilio** (cuenta de pago + saldo). *(Sección 3)*
4. **Crear el negocio como Enterprise** en el panel → se auto-provisiona TODO. *(Sección 5)*
5. **Verificar** que se creó el número y el agente de Retell. *(Sección 6)*
6. **Probar la voz** (llamar al número → María contesta). *(Sección 7)*
7. **Conectar y probar WhatsApp**. *(Sección 8)*
8. **Cargar datos del negocio** (servicios/precios) para que responda bien. *(Sección 9)*
9. **Verificar los límites Enterprise** y monitorear costos. *(Secciones 10–11)*

---

## 🌐 1. Conectar tu dominio `tuagentepro.xyz` a Railway

Ahora mismo tu app abre en `https://proyecto-agentepro-production.up.railway.app/`.
Vamos a que abra en `https://tuagentepro.xyz`.

1. En **Railway** → abre tu **servicio web** (el que sirve la app) → **Settings →
   Networking → Custom Domain** → escribe `tuagentepro.xyz`. (Opcional: agrega también
   `www.tuagentepro.xyz`.)
2. Railway te mostrará un **destino CNAME**, algo como `abcd1234.up.railway.app`.
   **Cópialo.**
3. Ve a donde compraste el dominio (tu **registrador**: Porkbun, Namecheap, GoDaddy,
   etc.) → zona **DNS**:
   - **Si usas `www`:** crea un registro **CNAME**, host `www`, valor = el destino de
     Railway.
   - **Para la raíz `@` (`tuagentepro.xyz` sin www):** muchos registradores **no**
     permiten CNAME en la raíz. Dos salidas:
     - (a) Usa el registro **ALIAS/ANAME** si tu registrador lo ofrece, apuntando al
       destino de Railway.
     - (b) **Recomendado:** pon el dominio en **Cloudflare** (gratis): cambia los
       *nameservers* del dominio a los de Cloudflare, y en Cloudflare crea un **CNAME**
       `@` → destino de Railway con la nube **naranja (proxied)**. Cloudflare resuelve
       el problema de la raíz.
4. **Espera** a que propague (de minutos a un par de horas). Railway emite el
   **certificado HTTPS solo** cuando detecta el DNS.
5. **Listo cuando:** `https://tuagentepro.xyz` abre tu landing, y
   `https://tuagentepro.xyz/health` devuelve `{"status":"healthy"}`.

> 💡 Mientras propaga, puedes seguir usando la URL `*.up.railway.app` para todo. Pero
> **no provisiones el negocio hasta tener el dominio listo** (o tendrás que rehacer los
> webhooks). Si tienes prisa, puedes provisionar con la URL de Railway y luego cambiar
> `FRONTEND_URL` — pero entonces hay que re-apuntar los webhooks a mano. Mejor: dominio
> primero.

---

## ⚙️ 2. Variables de entorno en Railway (CRÍTICO antes de provisionar)

En tu **servicio web** de Railway → pestaña **Variables**. Estas son las que importan
para que la auto-provisión funcione y grabe los webhooks correctos:

```
# La URL pública: de aquí sale la dirección de los webhooks de Twilio/Retell.
# DEBE ser tu dominio final, sin barra al final.
FRONTEND_URL = https://tuagentepro.xyz

# Cerebro (pon saldo en console.anthropic.com)
ANTHROPIC_API_KEY = sk-ant-...

# Twilio (cuenta de PAGO, ver Sección 3)
TWILIO_ACCOUNT_SID = AC...
TWILIO_AUTH_TOKEN  = ...

# Retell (la voz) — estos valores ya son los CORRECTOS y probados:
RETELL_API_KEY        = key_...
RETELL_LLM_MODEL      = claude-4.6-sonnet
RETELL_DEFAULT_VOICE_ID = cartesia-Hailey-Spanish-latin-america

# Producción
ENVIRONMENT = production
DEBUG = false
ALLOW_FREE_SIGNUP = false
```

> 🔴 **Lo más fácil de fallar:** si `FRONTEND_URL` está en `http://localhost:5173` (el
> valor por defecto), tu sistema configurará el webhook de voz de Twilio apuntando a
> *localhost* y **las llamadas nunca llegarán**. Por eso: **pon `FRONTEND_URL =
> https://tuagentepro.xyz` y guarda (deja que Railway redespliegue) ANTES de crear el
> negocio.**

Cómo lo arma el sistema (para que entiendas, del código):
- Webhook de voz de Twilio → `https://tuagentepro.xyz/webhooks/twilio/voice/{slug}`
- Webhook de Retell → `https://tuagentepro.xyz/webhooks/retell/{slug}`
- Webhook de WhatsApp (Twilio) → `https://tuagentepro.xyz/webhooks/twilio/whatsapp/{slug}`

*(El `{slug}` es el identificador único del negocio, ej. `mi-barberia-a1b2c3`.)*

**Verifica que las claves están activas:** entra a tu panel como Super Admin → el panel
muestra "salud de servicios". O abre
`https://tuagentepro.xyz/api/v1/admin/health` (con tu header de admin). Debe decir
`twilio: true`, `retell: true`, `anthropic: true`.

---

## 💳 3. Preparar Twilio (para que pueda COMPRAR el número de verdad)

Para que el sistema compre un número y reciba llamadas reales, tu cuenta Twilio debe
estar **en modo de pago (upgraded)**, no trial.

1. Entra a **console.twilio.com**.
2. Si dice **"Trial"** arriba: pulsa **Upgrade** y carga saldo (con US$20 te sobra para
   empezar; un número cuesta ~US$1–1.15/mes + el uso).
   - En trial: solo tienes 1 número, sale un aviso de "trial" en las llamadas y solo
     puedes llamar a números verificados. Por eso se sube a pago.
3. Anota tu **Account SID** (`AC...`) y **Auth Token** — deben ser los mismos que pusiste
   en Railway (Sección 2).

> 🌎 **Sobre el país del número:** el sistema intenta comprar un número de **Perú** y,
> si Twilio no tiene disponibles (lo normal, Perú es restringido), **compra uno de
> EE.UU. (+1)**. Para PROBAR está perfecto: un número +1 funciona igual para WhatsApp y
> para que María conteste. Si más adelante quieres un número peruano específico, se
> gestiona aparte con Twilio (trámite regulatorio).

---

## 🗑️ 4. (Si ya tienes un negocio de prueba) Bórralo para recrearlo bien

Como cambiar el plan **no** dispara la compra del número ni la creación del agente de
voz, para tu negocio real conviene partir limpio:

1. Entra a `https://tuagentepro.xyz/login` con tu cuenta de **Super Admin**.
2. Ve al panel **Super Admin → Negocios**.
3. Si quieres conservar los datos: usa **Exportar** (botón en la fila) → guarda el JSON.
4. Pulsa **Eliminar** en el negocio de prueba. *(Esto borra todos sus datos. Irreversible.)*

> Si tu único negocio nunca tuvo número/voz y no tiene datos importantes, bórralo sin
> miedo y créalo de nuevo en la Sección 5. Si SÍ tiene datos que quieres conservar, mira
> la **Sección 4b** (alternativa sin borrar).

### 4b. Conservar el negocio y agregarle/reconectar la voz (botón "Reconectar voz")
Si el negocio **ya tiene datos** (conversaciones, contactos) y NO quieres borrarlo —o si
**borraste por error su agente de Retell**— usa el botón **"Reconectar voz"** del panel
(ícono de teléfono 📞 en la fila del negocio, en Super Admin → Negocios):

1. Asegúrate de que el negocio tenga **plan con voz**: en su fila, cambia el plan a
   **Enterprise** (o Professional).
2. Pulsa el botón **"Reconectar voz"** (📞) en esa fila → confirma.
3. El sistema, sin tocar ningún dato:
   - Crea un **agente de Retell NUEVO** para ese negocio (descarta el anterior si quedó
     colgado).
   - Si el negocio **no tenía número Twilio**, **compra uno**; si ya tenía, **re-apunta
     su webhook de voz** al backend actual.
   - Guarda el `retell_agent_id` nuevo.
4. Verás un aviso con el nuevo `retell_agent_id` y el número. Verifícalo en Retell
   (Sección 6).

> Esto resuelve exactamente tu caso (agente de Retell borrado): **un clic y vuelve a
> tener voz**, conservando todos sus datos. Como cambiar de plan por sí solo NO
> re-provisiona la voz, este botón es la forma correcta de dárselo a un negocio
> existente.

> Si prefieres partir 100% limpio y el negocio no tiene datos importantes, también puedes
> borrarlo y recrearlo como Enterprise (Sección 5).

---

## 🏗️ 5. Crear el negocio como ENTERPRISE (auto-provisiona TODO)

Aquí ocurre la magia. Con las variables ya puestas (Sección 2) y Twilio de pago
(Sección 3):

1. Entra a `https://tuagentepro.xyz/login` como **Super Admin**.
2. Panel **Super Admin → Negocios → "Crear negocio"**.
3. Llena el formulario:
   - **Nombre del negocio:** el real (ej. *Barbería Don Pepe*).
   - **Tipo de negocio:** el rubro (barbería/servicios, salud, retail, etc.). Esto define
     las FAQs por defecto del agente.
   - **Plan: Enterprise.** ← clave, para que incluya voz + automatizaciones + reactivación.
   - **Email del dueño / Nombre del dueño / Teléfono del dueño** (este teléfono se usa
     como "escalar al dueño" cuando el cliente pide hablar con una persona).
   - **Contraseña** (si el formulario lo pide) o se genera una temporal.
4. Pulsa **Crear**. Espera unos segundos (está hablando con Twilio y Retell).

**Qué pasó automáticamente** (lo confirmé en el código):
- ✅ Se compró un **número Twilio** y se guardó en el negocio (`twilio_phone_number`).
- ✅ Se le configuró el **webhook de voz** apuntando a tu backend.
- ✅ Se creó el **agente de voz en Retell** y se guardó su `retell_agent_id`.
- ✅ Se crearon las **automatizaciones Enterprise**: *Seguimiento de leads*, *Reporte
  semanal* y *Reactivación de contactos inactivos*.
- ✅ Quedó con los **límites Enterprise**: 4,000 mensajes/mes y 150 llamadas/mes.

> Si el formulario del panel no tiene el campo "plan = Enterprise" al crear, créalo y
> luego en la fila del negocio usa **cambiar plan → Enterprise**. Los **módulos** se
> activan igual; el número/Retell ya se habrán creado si elegiste un plan con voz al
> momento de crear. Por eso, si puedes, **elige Enterprise (o Professional) desde el
> formulario de creación**.

---

## ✅ 6. Verificar que se creó el número y el agente de Retell

1. **En tu panel** (Super Admin → Negocios → abre el negocio, o en Uso y consumo): debe
   aparecer el **número de teléfono** asignado.
2. **En Twilio** (console → Phone Numbers → Manage → Active Numbers): debe estar el
   número nuevo, y al abrirlo, en **Voice → "A call comes in"** debe decir **Webhook** →
   `https://tuagentepro.xyz/webhooks/twilio/voice/{slug}` (POST).
3. **En Retell** (dashboard.retellai.com → Agents): debe aparecer un agente **"María"**
   nuevo (el de este negocio). Su `agent_id` es el que tu sistema guardó.

> 🛠️ **Si el número salió vacío** (Twilio estaba en trial al crear, o no había
> disponibilidad): el negocio igual se creó y el **agente de Retell también** (no
> depende del número). Solo te falta el número: cómpralo manual y apúntalo (Sección 7b).
> No hace falta recrear el negocio.

---

## ☎️ 7. Probar las LLAMADAS de voz (María)

### 7a. Prueba SIN gastar (web) — para oír a María ya
1. Entra a **dashboard.retellai.com** con tu cuenta de Retell.
2. **Agents → abre "María"** (la de tu negocio).
3. Pulsa **Test / Test Call** (ícono de micrófono 🎤) → permite el micrófono.
4. Háblale: *"Hola, ¿qué servicios tienen?"*, *"¿cuánto cuesta el corte?"*. María
   responde por voz con los datos del negocio.

> Esto prueba el cerebro de voz sin tocar el número de teléfono. Ideal para demos.

### 7b. Prueba REAL — llamar al número y que María conteste
1. Toma el **número Twilio** del negocio (Sección 6).
2. **Llámalo desde tu celular.**
3. María debe contestar y conversar.

**Si NO contesta o se corta**, revisa en orden:
- ¿El webhook de voz del número en Twilio apunta a
  `https://tuagentepro.xyz/webhooks/twilio/voice/{slug}` y es **POST**? *(Si compraste
  el número manual, configúralo aquí: número → Voice → "A call comes in" → Webhook →
  pega la URL → POST → Save.)*
- ¿`FRONTEND_URL` en Railway es `https://tuagentepro.xyz` (no localhost)?
- ¿El negocio tiene plan con voz, no está suspendido por pago, y no llegó al tope de 150
  llamadas? *(El sistema rechaza la llamada en esos 3 casos, a propósito, para no
  gastar de más.)*
- ¿`RETELL_API_KEY` activa y el agente "María" existe en Retell?

**Cómo conectarlo en el negocio real:** el dueño **desvía sus llamadas** al número
Twilio, o pone ese número en su Google Business / web, para que **las llamadas las
conteste María 24/7**.

---

## 💬 8. Conectar y probar WhatsApp

El número que se compró está configurado para **voz**. Para **WhatsApp** hay que
activarlo aparte. Dos caminos:

### 8a. RÁPIDO para probar HOY — Sandbox de Twilio (sin esperar a Meta)
1. Twilio console → **Messaging → Try it out → Send a WhatsApp message**.
2. Verás el número del **Sandbox** (normalmente **+1 415 523 8886**) y un código tipo
   `join algo-algo`.
3. Desde tu celular (WhatsApp), envía ese `join algo-algo` al número del Sandbox.
4. En esa página → **Sandbox settings** → campo **"When a message comes in"** pega:
   ```
   https://tuagentepro.xyz/webhooks/twilio/whatsapp/{slug}
   ```
   método **POST** → guarda. *(Reemplaza `{slug}` por el de tu negocio.)*
5. Escríbele al número del Sandbox: *"hola, ¿cuánto cuesta el corte?"* → **el robot
   responde**. Lo ves en vivo en tu panel → **Conversaciones**.

### 8b. PRODUCCIÓN — WhatsApp Sender real (tu número de negocio)
Para que los clientes escriban al **número propio del negocio** (no al Sandbox):
1. El negocio consigue un **chip nuevo** (línea **sin WhatsApp activo**) — o puedes usar
   el mismo número Twilio que se compró, registrándolo como sender.
2. Twilio console → **Messaging → Senders → WhatsApp senders → New WhatsApp Sender**.
3. Registra el número. Twilio hace el trámite con Meta por ti (nombre del negocio,
   categoría…). **Demora 1–3 días** hasta que Meta lo aprueba.
4. Cuando esté aprobado → en ese sender, campo **"When a message comes in"** pega:
   ```
   https://tuagentepro.xyz/webhooks/twilio/whatsapp/{slug}
   ```
   método **POST** → guarda.
5. Escríbele al número del negocio desde tu celular → el robot responde.

> El dueño **conserva su WhatsApp personal**: el robot atiende solo el número del
> negocio (chip nuevo o el de Twilio).

---

## 🛠️ 9. Cargar los datos del negocio (para que responda bien)

Para que María (chat y voz) dé precios y respuestas reales:

1. Entra al panel **del dueño** (no el de Super Admin) con la cuenta del negocio
   (`https://tuagentepro.xyz/login`).
2. Ve a **Agente IA / Configuración**:
   - **Servicios y precios** (ej. Corte S/25, Corte + barba S/35…).
   - **Horarios**, **dirección**, **FAQs**.
   - **Mensaje de bienvenida**.
   - **"Pasar con el dueño"**: agrega los números que, si escriben, el robot deriva al
     dueño con un mensaje fijo (sin gastar tokens).
3. *(Opcional)* Si usas **Notion como CRM**: en Configuración → "CRM en Notion", conecta
   tu base y pulsa **Sincronizar** (ver `docs/GUIA_NOTION_CRM.md`).

> La voz (Retell) usa estos mismos datos: cuando los cambias, el agente responde con la
> info nueva.

---

## 📊 10. Verificar que tiene TODO lo de Enterprise

En el panel **Super Admin → Negocios / Uso y consumo**, confirma para tu negocio:

| Debe tener | Cómo se ve |
|---|---|
| **Plan Enterprise** | etiqueta "Enterprise" en la fila |
| **4,000 mensajes/mes** | límite de mensajes del plan |
| **150 llamadas/mes** | límite de llamadas del plan |
| **Voz (María)** | número Twilio asignado + agente Retell |
| **Instagram IA, Citas, Contactos** | módulos desbloqueados (todo Professional) |
| **Reactivación de contactos** | automatización "Reactivación de contactos inactivos" activa |
| **Automatizaciones** | "Seguimiento de leads" + "Reporte semanal" activas |

En el panel **del dueño**, la barra lateral debe mostrar TODOS los módulos:
Conversaciones, Contactos, Citas, Instagram, Llamadas, Automatizaciones, Agente IA,
Configuración.

---

## 💵 11. Monitorear costos (para dormir tranquilo)

Lo que tú pagas (una tarjeta tuya en cada servicio). Pon **topes/alertas** en cada uno:

| Servicio | Dónde poner el tope |
|---|---|
| **Anthropic** | console.anthropic.com → Billing → Usage limits / alerts |
| **Twilio** | console.twilio.com → Billing → alertas de saldo + auto-recarga con tope |
| **Retell** | dashboard.retellai.com → Billing → límite de gasto |

Costos de referencia (de tu `PRICING.md`):
- 1 mensaje WhatsApp con IA ≈ **S/ 0.05**
- 1 llamada de voz (~3 min) ≈ **S/ 1.50** (lo más caro → por eso va topada a 150/mes)
- Número Twilio ≈ **S/ 4–8/mes**

Tu sistema **se protege solo**: rechaza llamadas/mensajes si el negocio está suspendido
por pago, si superó el tope del mes, o si el plan no incluye la función. Mira el consumo
real en el panel **Super Admin → Uso y consumo** (columna "Costo real") o en
`/api/v1/metrics/costs`.

---

## 🧯 12. Problemas comunes (troubleshooting)

| Síntoma | Causa probable | Solución |
|---|---|---|
| La llamada no entra / se corta | `FRONTEND_URL` mal (localhost) o webhook de voz mal | Pon `FRONTEND_URL=https://tuagentepro.xyz`, redeploy, y revisa el webhook del número en Twilio |
| Se creó el negocio pero **sin número** | Twilio estaba en trial o sin disponibilidad al crear | Sube Twilio a pago, compra el número manual y apúntalo (Sección 7b) |
| No aparece el agente "María" en Retell / lo borré por error | `RETELL_API_KEY` faltaba al crear, o se borró el agente | Pon la key y pulsa **"Reconectar voz"** (📞) en la fila del negocio (Sección 4b) — crea uno nuevo sin borrar datos |
| María contesta en inglés / voz rara | `RETELL_DEFAULT_VOICE_ID`/`RETELL_LLM_MODEL` mal | Usa `cartesia-Hailey-Spanish-latin-america` y `claude-4.6-sonnet` |
| WhatsApp no responde | webhook del Sandbox/Sender mal o slug equivocado | Revisa la URL `/webhooks/twilio/whatsapp/{slug}` (POST) en Twilio |
| El agente responde sin precios | Faltan datos del negocio | Cárgalos en Agente IA / Configuración (Sección 9) |
| El dominio no abre | DNS sin propagar o CNAME en la raíz no permitido | Usa Cloudflare para el `@` (Sección 1) |
| El dueño no puede entrar | No tiene su contraseña | Super Admin → Negocios → "Restablecer contraseña del dueño" |

---

## 🎯 13. Checklist final (táchalo)

```
DOMINIO
[ ] tuagentepro.xyz abre la app (https) y /health responde healthy

RAILWAY (variables)
[ ] FRONTEND_URL = https://tuagentepro.xyz
[ ] ANTHROPIC_API_KEY puesta + con saldo
[ ] TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN (cuenta de PAGO)
[ ] RETELL_API_KEY + RETELL_LLM_MODEL=claude-4.6-sonnet
    + RETELL_DEFAULT_VOICE_ID=cartesia-Hailey-Spanish-latin-america
[ ] /api/v1/admin/health → twilio:true, retell:true, anthropic:true

NEGOCIO ENTERPRISE
[ ] Creado desde Super Admin → Crear negocio, plan Enterprise
[ ] Tiene número Twilio asignado
[ ] Tiene agente "María" en Retell (retell_agent_id)
[ ] Webhook de voz del número → /webhooks/twilio/voice/{slug} (POST)
[ ] Automatizaciones activas: Seguimiento + Reporte semanal + Reactivación
[ ] Límites: 4,000 msg / 150 llamadas

VOZ
[ ] Probé en Retell (web Test): María habla ✅
[ ] Llamé al número Twilio: María contesta ✅

WHATSAPP
[ ] Sandbox o Sender configurado → /webhooks/twilio/whatsapp/{slug} (POST)
[ ] Le escribí: el robot responde ✅ (se ve en Conversaciones)

DATOS
[ ] Servicios/precios/horarios/FAQs cargados en Agente IA
[ ] "Pasar con el dueño" configurado

COSTOS
[ ] Topes/alertas puestos en Anthropic, Twilio y Retell
```

---

## 🔗 Guías relacionadas
- `docs/GUIA_DESPLIEGUE_RAILWAY.md` — despliegue y dominio (detalle técnico).
- `docs/GUIA_CONECTAR_CLIENTE_NUEVO.md` — el proceso por cada cliente que vendas.
- `docs/GUIA_LLAMADA_DE_VOZ.md` — probar a María paso a paso.
- `docs/GUIA_NOTION_CRM.md` — conectar Notion como base de datos del negocio.
- `agentepro/PRICING.md` — planes, precios y márgenes.
