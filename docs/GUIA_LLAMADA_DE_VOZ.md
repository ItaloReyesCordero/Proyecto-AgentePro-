# 🎙️ Probar la llamada de voz (María) — Guía paso a paso (bien detallada)

Esta guía te lleva de la mano para **escuchar al agente de voz** hablando con los
servicios y precios del negocio. Hay dos formas:

- **PARTE A — Llamada web de prueba** (la rápida): hablas con María por el
  **micrófono de tu computadora**. No cuesta comprar nada, ideal para probar YA.
- **PARTE B — Llamada por teléfono real** (para el despliegue): un cliente marca un
  número y María contesta. Necesita un número Twilio de voz; se hace al desplegar.

> 💡 Hazlo desde una **computadora con micrófono** (laptop sirve) y con audífonos
> para escuchar mejor.

---

## 🟩 PARTE A — Llamada web de prueba (hazla ahora)

### Paso 1 — Entra al panel de Retell

1. Abre tu navegador (Chrome) y entra a **https://dashboard.retellai.com**
2. Inicia sesión con **la misma cuenta de Retell** donde sacaste tu API key
   (la que está en tu `.env` como `RETELL_API_KEY`). Normalmente entras con Google
   o con tu correo.

### Paso 2 — Abre el agente "María"

1. En el menú de la **izquierda**, haz clic en **Agents** (Agentes).
2. En la lista verás un agente llamado **María**.
   - Su identificador es `agent_5f5cd078d34a87bae8ba8f2c38` (por si hay varios).
3. Haz clic en **María** para abrirlo.

### Paso 3 — Inicia la llamada de prueba

1. Con el agente abierto, busca el botón **"Test"** (arriba a la derecha o en un
   panel lateral). Puede aparecer como **"Test Audio"**, un **ícono de micrófono 🎤**
   o **"Test Call"**.
2. Haz clic en ese botón.
3. El navegador te pedirá permiso para usar el **micrófono** → haz clic en
   **Permitir** (Allow). *(Si no te lo pide y no se escucha, revisa el candado 🔒 de
   la barra de direcciones → Permisos → Micrófono → Permitir.)*

### Paso 4 — Habla con María

1. Cuando la llamada esté activa (verás un cronómetro o ondas de sonido), **habla
   normal**, por ejemplo:
   - *"Hola, ¿qué servicios tienen?"*
   - *"¿Cuánto cuesta el corte de cabello?"*
   - *"¿Y el corte con barba?"*
2. María te responde **por voz**, con los precios reales del negocio
   (corte S/25, corte + barba S/35, etc.).
3. Para terminar, haz clic en el botón rojo de **colgar** (Hang up / End).

🎉 ¡Listo! Acabas de escuchar a tu agente de voz funcionando.

> 💵 Cada minuto de prueba consume unos centavos de tu **saldo de Retell**. Es
> normal. Para pruebas cortas casi no se nota.

---

## 🧪 Qué deberías notar

- María habla en **español latinoamericano** (voz femenina).
- Conoce los **servicios y precios** del negocio (los mismos del panel / Notion).
- Si le preguntas algo que no sabe, deriva o pide hablar con una persona.

---

## ❓ Si algo sale mal (Parte A)

| Problema | Qué significa | Cómo arreglarlo |
|---|---|---|
| No veo el agente "María" | Entraste con otra cuenta de Retell | Cierra sesión y entra con la cuenta dueña de tu `RETELL_API_KEY` |
| No hay botón "Test" | La interfaz cambió de lugar | Busca un ícono de micrófono 🎤 o "Talk to agent" dentro del agente |
| No se escucha nada / no me oye | El navegador no tiene permiso de micrófono | Candado 🔒 en la barra → Micrófono → Permitir, y recarga |
| Se corta enseguida | Silencio prolongado | Habla apenas inicie; está configurado para colgar tras ~15s de silencio |
| Responde en inglés | (no debería) | Avísame y reviso el idioma del agente |

---

## 🟦 PARTE B — Llamada por teléfono real (para el despliegue)

Esto es para que un cliente **marque un número de verdad** y María conteste. Se deja
listo cuando despleguemos en Railway. Resumen de lo que implica (lo haremos juntos):

1. **Comprar un número Twilio con voz** (cuesta ~$1/mes). En tu consola de Twilio:
   **Phone Numbers → Buy a number** (elige uno con capacidad *Voice*).
2. **Apuntar el webhook de voz** de ese número a tu sistema:
   `https://tuagentepro.xyz/webhooks/twilio/voice/barberia-don-pepe-af0a24`
   (en Twilio: el número → sección *Voice* → "A call comes in" → Webhook → POST).
3. **Llamar al número** desde un celular → María contesta.

> ⚠️ Con cuenta Twilio de prueba (trial) solo puedes llamar a números **verificados**
> y la voz dice un aviso de "trial". Para producción se sube la cuenta a pago.
> Por eso la Parte B se hace en el despliegue, no en la laptop.

---

## 📌 Notas

- El agente de voz de un negocio se crea **automáticamente** cuando das de alta el
  negocio desde el panel **Admin → "Crear negocio"** (ahí también se le compra su
  número). Los negocios creados por el registro simple (como esta barbería de prueba)
  no lo tienen hasta provisionarlos.
- La voz, el idioma y el saludo se pueden ajustar después en el panel del negocio
  (sección de configuración de voz).
