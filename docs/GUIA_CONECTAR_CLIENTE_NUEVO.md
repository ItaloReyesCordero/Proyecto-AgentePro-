# 🚀 Guía para Vender y Conectar un Cliente Nuevo — AgentePro

> Guía operativa. La sigues **cada vez que vendes** a un negocio. Cubre WhatsApp,
> llamadas de voz, costos reales y márgenes. Pensada para que la abras en el momento
> y no te olvides de ningún paso.
>
> Última actualización: 2026-06-04

---

## 🧠 Lo que tienes que entender ANTES de vender (la idea base)

El robot **no se mete dentro del WhatsApp personal del cliente** (ese que abre en su
celular). WhatsApp no lo permite: **un número solo puede estar en UN WhatsApp a la vez**
— o en la app del teléfono, o en la API del robot, nunca en los dos al mismo tiempo.

Por eso el robot trabaja a través de la **WhatsApp Business API** (vía **Twilio**). Esto
te deja **2 formas de venderlo**:

| Escenario | Qué pasa | Cuándo usarlo |
|---|---|---|
| **A — Número nuevo dedicado** ⭐ | El cliente compra un **chip nuevo**. Ese número lo atiende el robot. El dueño conserva su WhatsApp personal intacto. | **Recomendado para vender ya.** Cero riesgo, cero interrupción. |
| **B — Su número de siempre** | Se **migra su número conocido** a la API. El robot lo atiende, pero el dueño pierde la app de WhatsApp normal en ese número. | Solo si el negocio insiste en su número conocido. Más trámite. Ofrécelo después. |

**Regla de oro para tus primeras ventas: vende siempre el Escenario A.** Evitas dolores
de cabeza con Meta (bloqueos, tokens que caducan).

---

## 💰 PARTE 1 — Cuánto te cuesta a TI (números reales)

Todo lo paga **una sola tarjeta tuya** conectada a 3 servicios. El cliente te paga la
mensualidad (por adelantado, Yape) y tú cubres esto. **Nunca pones plata primero.**

| Servicio | Para qué | A quién le pagas |
|---|---|---|
| **Anthropic** | Claude (el cerebro que escribe los mensajes) | siempre |
| **Twilio** | Los números + WhatsApp + llamadas | siempre |
| **Retell** | La voz con IA (María) que contesta llamadas | solo si vendes planes con voz |

### Costos FIJOS por número (mensual)
| Concepto | Costo real | En soles |
|---|---|---|
| Número Twilio (sirve para WhatsApp **y** voz) | ~$1.15 USD/mes | ~S/ 4 – 8 |

### Costos por USO
| Recurso | Costo real | En soles | Nota |
|---|---|---|---|
| 1 mensaje WhatsApp con IA | ~S/ 0.05 | barato | Claude + envío. Crece un poco con el historial. |
| 1 llamada de voz (~3 min) | ~S/ 1.50 | **el costo dominante** | Retell + Twilio. Por eso la voz va topada. |

> ⚠️ **La voz es lo caro.** Solo va en planes Professional (S/ 449) y Enterprise
> (S/ 799), **con tope de llamadas/mes**. El sistema corta la llamada solo cuando se
> llega al tope — no hay forma de que te desangres.

### Margen por cliente (a uso MÁXIMO del plan)
| Plan | Vendes (S/) | Te cuesta (S/) | **Ganas** |
|---|---|---|---|
| **Inicial** | 149 | ~14 | **~135 (91%)** |
| **Basic** | 249 | ~24 | **~225 (90%)** |
| **Professional** | 449 | ~173 | **~276 (61%)** |
| **Enterprise** | 799 | ~435 | **~365 (46%)** |

> Ese "te cuesta" es al **100% del tope**. Casi ningún cliente llega ahí, así que en la
> práctica **ganas más**. Valida el consumo real en `/api/v1/metrics/costs` y en el
> panel del fundador (`/admin/analytics`, columna "Costo real").

**Break-even ≈ 1 cliente.** Con un solo Basic ya cubres Railway + dominio (~S/ 80–120/mes).

---

## ✅ PARTE 0 — Requisitos que debes tener listos UNA sola vez

Antes de tu primer cliente, ten esto montado (no se repite por cliente):

- [ ] **1 cuenta Twilio** (tuya, para TODOS tus clientes) con tarjeta + **tope de gasto y alerta**.
- [ ] **1 cuenta Anthropic** (Claude) con autorecarga + tope.
- [ ] **1 cuenta Retell** (solo si venderás voz) con tope.
- [ ] **Backend desplegado en Railway** con **dominio fijo** (los webhooks necesitan una URL estable, no un túnel temporal).

> 💡 Sin dominio fijo, cada vez que se reinicie el túnel se cae la conexión. Para vender
> en serio: **despliega en Railway** (ver `docs/GUIA_DESPLIEGUE_RAILWAY.md`).

---

## 📱 PARTE 2 — Conectar el WhatsApp de un cliente nuevo

Ruta recomendada: **Twilio WhatsApp Sender + número dedicado** (Escenario A).

### Antes de empezar
El cliente consigue un **chip nuevo** (una línea **sin WhatsApp activo**). Ese número
será "el WhatsApp del robot". Su WhatsApp personal **no se toca**.

### Pasos

1. **Da de alta el negocio en tu panel:**
   `Admin → Crear negocio`. Esto genera su **`slug` único** (ej. `barberia-don-pepe-af0a24`).
   👉 Anota el slug, lo usarás en el webhook.

2. **Entra a Twilio Console** → `Messaging → Senders → WhatsApp senders → New sender`.

3. **Registra el número del chip nuevo** del cliente. Twilio inicia el trámite con Meta
   por ti (te pedirá nombre del negocio, categoría, etc.).
   ⏳ **Demora 1–3 días** hasta que Meta lo aprueba.

4. **Cuando esté aprobado**, en ese sender → campo **"When a message comes in"** pega:
   ```
   https://TU-DOMINIO/webhooks/twilio/whatsapp/EL-SLUG-DEL-NEGOCIO
   ```
   Método **POST**. Guarda.
   *(Ejemplo real: `https://tuagentepro.xyz/webhooks/twilio/whatsapp/barberia-don-pepe-af0a24`)*

5. **Prueba:** escribe al número del cliente desde tu celular (ej. *"hola, ¿cuánto cuesta
   el corte?"*) → **el robot responde**. Lo ves en vivo en tu panel → **Conversaciones**.

✅ **Listo.** El robot atiende el WhatsApp del negocio; el dueño conserva el suyo personal.

### 🎬 Para DEMOS rápidas (vender sin esperar a Meta)
Usa el **Sandbox de Twilio** (número compartido, gratis, funciona al instante):

1. Twilio Console → `Messaging → Try it out → Send a WhatsApp message`.
2. Verás el número del Sandbox (normalmente **+1 415 523 8886**) y un código tipo `join algo-algo`.
3. Desde tu celular, envía ese `join algo-algo` al número del Sandbox.
4. En la misma página → `Sandbox settings` → campo **"When a message comes in"** pega:
   `https://TU-DOMINIO/webhooks/twilio/whatsapp/EL-SLUG` (POST) → guarda.
5. Escribe al número del Sandbox → el robot responde. 🎉 **Ideal para mostrarle al cliente
   que funciona HOY**, antes de pedir el sender real.

---

## 📞 PARTE 3 — Conectar las llamadas de voz (María)

La voz usa **Twilio (el número que marca el cliente) + Retell (el cerebro que habla)**.
Solo aplica a planes **Professional y Enterprise**.

### Lo bueno: tu panel lo automatiza
Cuando creas el negocio en `Admin → Crear negocio`, el sistema **compra el número Twilio
y crea el agente de voz de Retell solo** (queda guardado como `retell_agent_id` del
negocio). Normalmente no tienes que hacer nada manual.

### Verificación / configuración manual (si hace falta)

1. El negocio debe tener **plan con voz** y un **número Twilio con capacidad *Voice***.
2. En Twilio, ese número → sección **Voice → "A call comes in"** → Webhook → POST:
   ```
   https://TU-DOMINIO/webhooks/twilio/voice/EL-SLUG-DEL-NEGOCIO
   ```
3. **Prueba:** llama a ese número desde un celular → **María contesta** con los precios
   reales del negocio.

### Cómo venderlo
El negocio **desvía sus llamadas** (o pone el número Twilio en su web / ficha de Google)
para que las **llamadas perdidas las conteste María 24/7**. Cada llamada cuesta ~S/ 1.50
y está topada por plan, así que el margen está protegido.

### 🎬 Probar la voz sin comprar nada (para demos)
Dashboard de Retell → agente "María" → botón **Test** → hablas por el micrófono de tu
laptop. Le muestras al cliente cómo suena **sin gastar en número**.

### 🛡️ Protección de costos automática
El sistema **rechaza la llamada** (sin gastar tu plata) si:
- la cuenta está bloqueada (prueba vencida / impago), **o**
- el plan no incluye voz, **o**
- ya se llegó al **tope de llamadas del mes**.

Así nunca te sorprende un recibo.

---

## 🗺️ Resumen visual del flujo (qué pasa por dentro)

```
Cliente escribe/llama al número del negocio
        │
        ▼
  Twilio / Meta  ──(reenvía)──►  Webhook de tu backend
                                  /webhooks/twilio/whatsapp/{slug}   (texto)
                                  /webhooks/twilio/voice/{slug}      (voz)
        │
        ▼
  Tu robot identifica el negocio por su {slug}
        │
        ├─ WhatsApp: Claude piensa y responde desde el MISMO número
        └─ Voz: conecta con Retell (María) que habla en tiempo real
        │
        ▼
  Todo queda registrado en tu panel → Conversaciones / Llamadas
```

> Un **solo sistema** atiende a **muchos clientes a la vez**: cada negocio se distingue
> por su `{slug}` en la URL del webhook.

---

## 📋 Checklist por cada cliente nuevo (imprímelo / cópialo)

```
NEGOCIO: ____________________   PLAN VENDIDO: ____________   PAGÓ (Yape): [ ]

[ ] Cobré la mensualidad por adelantado
[ ] Creé el negocio en Admin → Crear negocio   → slug: ____________________
[ ] Cargué sus datos (servicios, precios, horarios) en el panel
WHATSAPP
[ ] Cliente consiguió chip nuevo                → número: ____________________
[ ] Creé el WhatsApp Sender en Twilio
[ ] Meta aprobó el sender (1–3 días)
[ ] Pegué el webhook /webhooks/twilio/whatsapp/{slug} (POST)
[ ] Probé: el robot responde ✅
VOZ (solo Professional / Enterprise)
[ ] Número Twilio con Voice asignado
[ ] Webhook /webhooks/twilio/voice/{slug} configurado
[ ] retell_agent_id creado (auto al crear el negocio)
[ ] Probé: María contesta ✅
[ ] Le mostré al cliente su panel (Conversaciones / Citas / Llamadas)
```

---

## ❓ Problemas comunes

| Problema | Causa probable | Solución |
|---|---|---|
| El robot no responde WhatsApp | Webhook mal pegado o slug equivocado | Revisa la URL en Twilio: debe terminar en el slug correcto y ser POST |
| Meta no aprueba el sender | Datos del negocio incompletos | Completa nombre/categoría reales en Twilio y reenvía |
| La llamada dice "no disponible" | Plan sin voz, tope alcanzado o cuenta bloqueada | Verifica plan, uso del mes y estado de pago del negocio |
| Dejó de responder al día siguiente | Usaste túnel temporal o token de prueba de Meta | Despliega en Railway con dominio fijo (no túnel) |
| Quiero probar sin esperar a Meta | — | Usa el **Sandbox de Twilio** (Parte 2, sección Demos) |

---

## 🔗 Guías relacionadas
- `docs/GUIA_DESPLIEGUE_RAILWAY.md` — desplegar el backend con dominio fijo.
- `docs/GUIA_LLAMADA_DE_VOZ.md` — probar a María paso a paso.
- `docs/PLAN_COBRO_MANUAL.md` — cómo cobrar (Yape, por adelantado, sin Culqi).
- `agentepro/PRICING.md` — planes, precios y márgenes al detalle.
- `docs/MANUAL_DE_VENTAS.md` — argumentos de venta.
