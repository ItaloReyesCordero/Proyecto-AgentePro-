# 📅 Citas automáticas, avisos al dueño y recordatorios

AgentePro ahora **detecta solo** cuando un cliente quiere agendar (por WhatsApp,
Instagram o llamada), **registra la cita**, **avisa al dueño** y **recuerda al
cliente** antes de la hora. Aquí está cómo funciona y cómo usarlo.

## ¿Cómo funciona? (en simple)

1. Un cliente escribe/llama: *"Quiero una cita de solo barba el viernes a las 5"*.
2. El agente IA entiende que es una cita y **la crea** con: servicio, día/hora,
   nombre y teléfono del cliente.
3. Al dueño le llega un **aviso**: en el panel (sección **Citas**), por **email**, y
   por **WhatsApp** (si está configurado su número).
4. El cliente recibe un **recordatorio automático por WhatsApp** unas horas antes
   (configurable, por defecto 24h) pidiéndole confirmar.
5. El dueño ve todo en **Panel → Citas** y puede **Confirmar / Completar / Cancelar**.

> El agente entiende lenguaje natural ("mañana", "el viernes", "pasado a las 3").
> Si el cliente no dice la hora exacta, la cita queda como "por coordinar" igual.

## Dónde verlas

Panel del negocio → menú izquierdo → **Citas**. Cada cita muestra el servicio,
cliente, cuándo, de qué canal vino (WhatsApp/Instagram/Llamada/Manual) y su estado:

- **Solicitada** — el cliente la pidió (falta que el negocio confirme).
- **Confirmada** — el negocio la aceptó.
- **Completada** — ya se atendió.
- **Cancelada**.

También puedes crear una cita **a mano** con el botón **"Nueva cita"**.

## Avisos al dueño

Cuando entra una cita nueva, el dueño recibe:
- 🔔 Aviso en el panel en tiempo real (y aparece en **Citas**).
- 📧 **Email** (si configuraste el correo de escalamiento del agente).
- 💬 **WhatsApp** al número del dueño (campo "teléfono de escalamiento" del agente,
  o el WhatsApp de contacto de pagos). Es "mejor esfuerzo": si ese número no está
  disponible, igual quedan el panel y el email.

## Recordatorios automáticos

Una tarea programada revisa cada hora las citas próximas y envía un WhatsApp al
**cliente** recordándole, una sola vez por cita.

⚙️ **Requiere el proceso `beat` de Celery corriendo** (el planificador). En el
`docker-compose.yml` ya se agregó el servicio `beat`. En el despliegue, asegúrate de
tener un proceso `celery -A app.workers.celery_app beat` además del `worker`.

La ventana de recordatorio (horas antes) se ajusta con `REMINDER_WINDOW_HOURS` en
`.env` (por defecto 24).

## Límites honestos (qué NO hace todavía)

- No revisa **choques de horario** ni "huecos" disponibles (no es un calendario con
  disponibilidad; registra lo que el cliente pide). El dueño confirma/coordina.
- No se integra (aún) con Google Calendar. Las citas viven en AgentePro.
- El recordatorio por WhatsApp al cliente usa Twilio/Meta del negocio; con el sandbox
  de Twilio, el cliente debe haber escrito al número (estar "unido") para recibirlo.

## Para desarrolladores

- Modelo: `app/models/appointment.py` (tabla `appointments`, migración `006_appointments`).
- Detección: `app/services/appointment_service.py` (`maybe_create_from_agent`,
  `parse_when`), enganchada en `whatsapp/webhook_handler.py` (chat) y
  `voice/call_handler.py` (llamadas, vía el resumen de la llamada).
- Aviso al dueño: `notify_owner_new_appointment` (socket + Resend + WhatsApp).
- Recordatorios: `app/workers/reminder_tasks.py::_send_reminders` (beat cada hora).
- API: `GET/POST/PATCH/DELETE /api/v1/appointments`. UI: página **Citas**.
