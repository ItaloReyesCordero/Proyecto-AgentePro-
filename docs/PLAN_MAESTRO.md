# Plan Maestro — AgentePro 2.0

> Revisión completa del sistema, arquitectura de voz, mejoras de UX y hoja de ruta.
> Todo verificado leyendo el código real el 2026-06-01. Nada inventado.

---

## A. Revisión completa: estado real de cada parte

### ✅ Lo que está hecho y funciona (verificado)
- **Backend completo**: 85 rutas, 18 tests pasan. Auth, tenants, agente, voz, llamadas, contactos, conversaciones, Instagram, automatizaciones, métricas, admin, provisioning, webhooks (Meta/Retell/Twilio/Culqi).
- **Frontend completo y conectado a datos reales**: las páginas (Dashboard, Contactos, Conversaciones, Llamadas, Instagram, Automatizaciones, Agente IA, Configuración) usan hooks (`useContacts`, `useConversations`, `useCalls`, etc.) que llaman a la API de verdad. **No son cascarones.**
- **Multi-tenant**: una sola BD Postgres, aislada por `tenant_id`. Cada negocio tiene su slug, su webhook y sus credenciales cifradas.
- **Panel Super Admin** (`/app/admin`): métricas globales, crear negocio, cambiar plan, activar/desactivar, **exportar** y **eliminar** datos, reiniciar uso.
- **Onboarding** con conexión de WhatsApp real.
- **Bloqueo de trial**: al vencer, dashboard 402 → pantalla de renovación, el agente deja de responder, no hay llamadas.
- **"Probar agente"** en vivo dentro del dashboard (no necesita WhatsApp, solo Anthropic).

### ⚠️ Lo que está implementado pero NO se puede probar sin keys
Esto **no está roto**; simplemente no hace nada hasta poner la key:
- **Respuestas de IA** → necesita `ANTHROPIC_API_KEY`. Sin ella, el agente contesta "tuve un problema técnico".
- **WhatsApp real** → necesita credenciales Meta del cliente + URL pública (no localhost).
- **Voz** → necesita Twilio + Retell.
- **Instagram / audios / CRM / emails / cobro** → fal.ai / OpenAI / HubSpot / Resend / Culqi.

### 🔴 Riesgos y cosas a vigilar (importantes antes de cobrar)
1. ✅ **Aislamiento forzado en la capa de datos (resuelto 2026-06-01).** `app/core/tenant_scope.py` aplica automáticamente el filtro `tenant_id` a toda consulta SELECT de un negocio autenticado (listener `do_orm_execute` + `with_loader_criteria`). Un endpoint que olvide filtrar **ya no puede** filtrar datos de otro negocio. Verificado contra Postgres real (negocio normal sigue OK) y con prueba de fuga (pedir dato de otro negocio → vacío). *Pendiente como capa extra:* RLS **nativo** de Postgres con un rol de BD restringido — se activa en el despliegue de producción (ahí se prueba sin arriesgar el flujo de WhatsApp en vivo).
2. **Webhook de WhatsApp sin firma si falta `META_APP_SECRET`.** En dev acepta todo; en producción **debes** poner `META_APP_SECRET` o cualquiera podría inyectar mensajes falsos.
3. **`bcrypt` local desalineado.** El Python global de tu laptop tenía bcrypt 5.0 (rompe el login). El proyecto fija `bcrypt==4.0.1`. **Docker está bien** (instala desde el pyproject). Solo afecta si corres el backend fuera de Docker.
4. **`email-validator` rechaza dominios reservados** (`.local`, etc.). Los clientes deben usar emails reales.
5. **Backups son globales** (una sola BD). No hay restauración por-cliente; el export por-cliente ya ayuda para bajas.
6. **Placeholder pendiente**: el botón de la pantalla "prueba vencida" apunta a `wa.me/51999999999`. Cambiar por tu número/checkout real.

### 🧪 Qué puedes probar HOY (sin desplegar, sin keys de pago)
- Login como Super Admin → crear negocio → exportar → eliminar.
- Registrar un negocio (trial) → onboarding → ver su dashboard (vacío) → configurar agente.
- Ver el bloqueo de trial (cambiando la fecha o el plan).
- **Con solo `ANTHROPIC_API_KEY`**: el botón "Probar agente" responde de verdad. Esta es la forma más rápida de "ver la magia" sin montar WhatsApp.

---

## B. Arquitectura de voz: ¿un bot por negocio o uno para todos?

**Cada negocio tiene su PROPIO agente de voz IA.** No hay un solo bot compartido.

Cómo funciona (verificado en el código):
1. Al dar de alta un negocio, el provisioner crea en **Retell** un *LLM* + un *agente de voz* exclusivos para ese negocio, con su propio prompt (nombre, horario, FAQs). Se guarda `tenant.retell_agent_id`.
2. También se le asigna su **propio número de Twilio**.
3. **Llamada entrante**: el número del negocio → webhook `/webhooks/twilio/voice/{slug}` → el sistema responde con TwiML que conecta el audio a `wss://api.retellai.com/audio-websocket/{retell_agent_id}` — es decir, **al agente de ESE negocio**.
4. **Llamada saliente**: se usa `override_agent_id` con el agente de ese negocio.

### ¿Hay interferencia? ¿El bot puede atender a 2 personas a la vez?
**Sí puede, sin problema.** Retell es un servicio en la nube: cada llamada es una **sesión independiente**. Si 5 personas llaman al mismo negocio a la vez, son 5 sesiones simultáneas del mismo agente — no se pisan. No es "un robot físico" que solo puede hablar con uno.

El único límite real es:
- La **concurrencia de tu plan de Retell** (cuántas llamadas simultáneas permite tu cuenta) y de **Twilio**.
- Todo corre bajo **tu** `RETELL_API_KEY` y **tu** cuenta de Twilio (una sola), pero con un agente y un número **distintos por negocio**. Tú pagas el uso; cada cliente tiene lo suyo aislado.

**Resumen:** 1 agente de voz + 1 número por negocio · llamadas simultáneas sí · sin interferencia · límite = tu plan de Retell/Twilio.

---

## C. Mejoras de UX fáciles y útiles (propuestas, sin keys)

Ordenadas por impacto/esfuerzo. Todas mejoran lo "fácil de usar" para el cliente:

1. **Indicador de estado de WhatsApp en el dashboard** (conectado / desconectado + botón reconectar). Hoy se ve en Configuración; ponerlo visible ayuda a que el cliente sepa si su agente está "vivo". *Fácil.*
2. **Checklist de activación en el dashboard** ("1. Conecta WhatsApp ✅ · 2. Configura tu agente ⬜ · 3. Pruébalo ⬜"). Guía al cliente a activar todo. *Fácil.*
3. **Banner de trial** (✅ ya hecho) — avisa días restantes.
4. **Botón "Enviarme un WhatsApp de prueba"** una vez conectado, para que el cliente compruebe que recibe/responde. *Medio.*
5. **Mensajes vacíos amables** ("Aún no tienes conversaciones — cuando un cliente te escriba por WhatsApp aparecerá aquí"). Evita que el dashboard se vea "roto" al inicio. *Fácil.*
6. **Onboarding: poder configurar el agente (nombre/FAQs) en el mismo flujo**, no solo conectar WhatsApp. *Medio.*
7. **Pantalla de planes/upgrade self-service** para el cliente (ver su plan, uso del mes, y pedir cambio). *Medio.*
8. **Tu número de contacto real** en la pantalla de "prueba vencida". *Trivial.*

> Recomendación: hacer 1, 2, 5 y 8 (rápidas, alto impacto en percepción) antes de meter keys.

---

## D. Hoja de ruta (fases)

### Fase 0 — Pulido sin keys (ahora) ✅/⬜
- ✅ Trial que expira y bloquea
- ✅ Crear/exportar/eliminar negocios desde el panel
- ✅ Banner de trial
- ⬜ Mejoras UX 1, 2, 5, 8 de la sección C
- ⬜ Cambiar placeholder de WhatsApp por tu contacto real

### Fase 1 — Encender la inteligencia (1 key)
- ⬜ Poner `ANTHROPIC_API_KEY` y probar el agente en vivo (botón "Probar agente")
- ⬜ Afinar el prompt/FAQs por rubro si hace falta

### Fase 2 — Vender WhatsApp (requiere despliegue)
- ⬜ Desplegar backend+frontend en un servidor con **dominio público HTTPS**
- ⬜ Poner `META_APP_SECRET` y completar la app de Meta
- ⬜ Endurecer `.env`: `SECRET_KEY` nuevo, `DEBUG=false`, `ENVIRONMENT=production`, `FRONTEND_URL` real
- ⬜ Onboardear el primer cliente real y validar un mensaje de ida y vuelta

### Fase 3 — Cobro automático
- ⬜ Cablear Culqi en el registro (`/signup` + widget) y poner `ALLOW_FREE_SIGNUP=false`
- ⬜ Pantalla de billing/upgrade self-service

### Fase 4 — Add-ons (según demanda)
- ⬜ Voz (Twilio + Retell) · Instagram (fal.ai) · audios (OpenAI) · CRM (HubSpot) · emails (Resend)

### Fase 5 — Robustez para escalar
- ⬜ Backups automáticos de Postgres
- ⬜ Revisar aislamiento por tenant / considerar RLS
- ⬜ Monitoreo y alertas

---

## E. Cómo conseguir las API keys
Ver **`docs/COMO_CONSEGUIR_API_KEYS.md`** (paso a paso por cada una).
