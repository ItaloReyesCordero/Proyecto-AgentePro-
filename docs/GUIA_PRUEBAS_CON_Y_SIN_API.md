# Guía de pruebas — CON y SIN API keys

> Qué probar paso a paso y **cómo debe comportarse cada cosa** en dos escenarios:
> (A) **SIN** las API keys (estado actual, antes de contratar nada) y
> (B) **CON** las API keys ya contratadas (producción real).
> Complementa a `MANUAL_DE_PRUEBAS.md` (ese tiene el checklist por módulo).
> Fecha: 2026-06-03.

---

## Cómo saber qué APIs tienes puestas
En `/app/admin → Dashboard → "Estado de servicios"`. Cada chip:
- **✓** = la API key está configurada (ese servicio funciona).
- **—** = falta (ese servicio NO funcionará, pero **la app no se rompe**, solo degrada con un mensaje).

Las keys viven en `agentepro/backend/.env`. Tras editarlas: `docker compose restart backend`.

---

## Tabla resumen: qué funciona en cada escenario

| Función | SIN API keys (hoy) | CON API keys |
|---|---|---|
| Login / panel admin / panel dueño | ✅ Funciona | ✅ Funciona |
| Crear/activar/desactivar/eliminar negocio | ✅ Funciona | ✅ Funciona |
| Cobros (Yape manual) y recuperación de clave | ✅ Funciona | ✅ Funciona |
| Editar y guardar config del agente | ✅ Funciona | ✅ Funciona |
| **"Probar agente"** (chat de prueba) | ⚠️ Devuelve "verifica ANTHROPIC_API_KEY" | ✅ Responde con IA |
| **Recibir/responder WhatsApp real** | ❌ No (necesita Meta) | ✅ Funciona |
| **Llamadas de voz** | ❌ No (necesita Twilio+Retell) | ✅ Funciona |
| **Generar posts de Instagram (imagen)** | ❌ No (necesita fal + Claude) | ✅ Funciona |
| **Resúmenes de llamada con IA** | ⚠️ "No se pudo generar" | ✅ Funciona |
| **Sincronizar CRM (HubSpot)** | ❌ No (opcional) | ✅ Funciona |
| **Enviar correos** | ❌ No (opcional, Resend) | ✅ Funciona |
| Cobro automático con tarjeta (Culqi) | 🚫 Apagado a propósito (usas Yape) | 🚫 Sigue apagado hasta que tú quieras |

> Regla de oro: **nada se rompe** sin las keys. Lo que necesita una key externa simplemente
> muestra un mensaje claro o no hace la acción, pero el sistema sigue de pie.

---

## ESCENARIO A — SIN API keys (lo que puedes probar HOY)

### A.1 Todo el panel de administración (tú)
1. Login super admin → entra a **Admin**.
2. Recorre las 5 pestañas. **Debe verse todo sin errores** (los números pueden ser 0).
3. **Crear un negocio de prueba** → aparece en la lista.
4. **Desactivar** ese negocio → su dueño, al entrar, ve "Tu servicio está en pausa".
5. **Activar** → su dueño vuelve a entrar.
6. **Eliminar** el negocio de juguete.
> ✅ Esto NO necesita ninguna API. Si algo falla aquí, es un bug real (avísame).

### A.2 Panel del dueño (cliente)
1. Login como dueño demo.
2. Dashboard, Conversaciones, Contactos, Automatizaciones, Llamadas, Ajustes: **todo carga** (listas vacías está bien).
3. **Agente IA → editar el prompt → Guardar:** debe guardar sin error.
4. **Agente IA → "Probar agente":** escribe un mensaje y envía.
   - SIN key: responde **"No se pudo generar la respuesta de prueba (verifica ANTHROPIC_API_KEY)"**. ✅ Eso es lo esperado.
5. Cambia tema claro/oscuro y color de marca en Ajustes: debe aplicarse al instante.

### A.3 Flujo de prueba/pago
1. Deja vencer (o suspende) un trial → el dueño ve la pantalla de Yape con tus datos.
2. En Admin → Cobros → "Marcar pagado": reactiva y mueve el vencimiento un mes.

**Conclusión del escenario A:** todo el "esqueleto" del negocio (gestión, multi-tenant, cobros,
seguridad de acceso) se prueba **sin gastar un sol en APIs**. Lo único que no puedes ver es la IA
respondiendo de verdad.

---

## ESCENARIO B — CON API keys (cuando ya contrataste)

> Orden recomendado de contratación: **1) Anthropic (Claude)** → 2) WhatsApp (Meta) →
> 3) Voz (Twilio+Retell) → 4) opcionales (fal, HubSpot, Resend).

### B.1 Con SOLO Anthropic (Claude) puesta
Es el mínimo para vender el producto. Pon `ANTHROPIC_API_KEY` → `restart backend`.
1. Estado de servicios: `anthropic ✓`.
2. **Probar agente:** escribe "Hola, ¿qué venden?" → **debe responder con IA** según el prompt del negocio.
3. Edita el prompt (ej. "eres una cafetería, vendes café") → vuelve a probar → la respuesta cambia.
4. En Admin → Uso y consumo: tras varias pruebas, sube el contador de **mensajes** y el **costo Claude $** del negocio.
> ✅ Con esto ya puedes hacer demos a clientes mostrando el agente respondiendo.

### B.2 Con WhatsApp (Meta Cloud API) por cliente
Cada negocio conecta SU número. En el onboarding (paso 2) o en Ajustes → WhatsApp.
1. Conecta el `phone_number_id` + token del cliente. Estado: `meta_whatsapp ✓`.
2. Configura el webhook en Meta apuntando a `https://TU-DOMINIO/webhooks/whatsapp/{slug}` con el verify token.
3. **Prueba real:** desde otro celular, escribe al WhatsApp del negocio.
   - Debe aparecer la conversación en el panel del dueño (tiempo real).
   - El agente debe **responder solo** con IA (si el bot está activo y el negocio no está suspendido).
4. Marca la conversación como "tomar control humano" → el bot deja de responder esa conversación.
5. **Prueba de bloqueo:** desactiva el negocio en Admin → escribe de nuevo → el mensaje se guarda pero **el agente NO responde**. Reactiva → vuelve a responder.

### B.3 Con Voz (Twilio + Retell)
1. Cada negocio recibe su número Twilio + su agente Retell al aprovisionarse. Estado: `twilio ✓` `retell ✓`.
2. **Llamada entrante:** llama al número del negocio → debe contestar el agente de voz en español.
3. **Llamada saliente:** Agente IA → "Probar llamada" (o automatización) → debe llamar a un lead.
4. Tras la llamada, en Llamadas debe aparecer el registro y (con Claude) un **resumen automático**.

### B.4 Opcionales
- **fal (`FAL_KEY`):** Instagram → "Generar post" → crea imagen + texto → Aprobar → Publicar.
- **HubSpot:** los contactos/leads se sincronizan al CRM del cliente.
- **Resend:** se envían correos (notificaciones).

---

## Qué revisar tras contratar TODO (checklist final pre-venta)
- [ ] Estado de servicios: todo en ✓ (menos culqi, que sigue apagado a propósito).
- [ ] Probar agente responde con IA.
- [ ] WhatsApp real: recibe y responde.
- [ ] Desactivar negocio → corta WhatsApp + panel; reactivar → vuelve.
- [ ] Llamada de voz entrante y saliente.
- [ ] Uso y consumo refleja mensajes/llamadas/costo por negocio.
- [ ] Cobro Yape: marcar pagado mueve el vencimiento y reactiva.
- [ ] Backups corriendo (`agentepro/backups/` con archivos `.dump`).

---

## Nota sobre Culqi (cobro con tarjeta)
**NO necesitas Culqi.** El sistema está diseñado para que cobres **manual por Yape/transferencia,
por adelantado**. Culqi está en el código pero **apagado** (sin keys no hace nada). Lo activas
recién cuando tengas volumen y quieras cobro automático con tarjeta. El "-48", el MRR, etc. NO
dependen de Culqi para nada.
