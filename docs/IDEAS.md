# Ideas para AgentePro 2.0

> Backlog de mejoras (frontend + backend). Cada idea está aterrizada en lo que ya
> existe en el sistema. **No es una promesa de hacerlas todas** — es un menú para ir
> eligiendo.
>
> **Leyenda:** 🟢 fácil · 🟡 medio · 🔴 grande · 🔑 necesita una API key ·
> ⭐ alto valor / bajo esfuerzo (recomendado) · ✅ ya hecho · ⚙️ el backend ya lo
> soporta, falta la UI.

---

## ⭐ Recomendado para empezar (sin keys, bajo riesgo, alto impacto)

> **Tanda implementada el 2026-06-01:** F1, F2, F6, F7, A1, A5, S6 ✅ (build OK, 86 rutas, lógica verificada en runtime).

- ✅ Indicador **WhatsApp conectado/desconectado** en el dashboard (#F1)
- ✅ **Checklist de activación** del negocio (#F2)
- ✅ **Estados vacíos amables** (#F4) — el componente `EmptyState` ya existía
- ✅ **Notificaciones en tiempo real** (toasts: mensaje entrante + escalado) (#F6)
- ✅ **Buscador** en Contactos (#F7)
- ✅ **Buscar clientes** en el panel admin (#A1)
- ✅ **Visor de logs de webhooks** por cliente (#A5)
- ✅ Endurecer **webhook de WhatsApp** (rechaza sin `META_APP_SECRET` en prod) (#S6)
- ⬜ **Ver el prompt del agente** — el backend ya lo expone (#F18) ⚙️ *(pendiente)*
- ⬜ Poner tu **contacto real** en la pantalla de "prueba vencida" (#F3) — *me falta tu número de WhatsApp/checkout*

---

## 1. Frontend — Cliente (dueño del negocio)

| # | Idea | Esf. | Notas |
|---|---|---|---|
| F1 | Indicador **WhatsApp conectado/desconectado** en el dashboard | ✅ | hecho 2026-06-01 (`ActivationCard`) |
| F2 | **Checklist de activación** ("conecta WhatsApp · configura agente · pruébalo") | ✅ | hecho 2026-06-01 (`ActivationCard`) |
| F3 | Poner **contacto real** en la pantalla `/app/upgrade` (hoy placeholder) | 🟢 | trivial |
| F4 | **Estados vacíos amables** + skeletons de carga | ✅/🟢 | el componente `EmptyState` ya existe y se usa; *skeletons de carga: pendiente* |
| F5 | **Banner de días de trial** | ✅ | ya implementado |
| F6 | **Notificaciones en tiempo real (toasts)** | ✅ | hecho 2026-06-01: toast en mensaje entrante de cliente + escalado (`useSocket`) |
| F7 | **Buscador** en Contactos (nombre/teléfono) | ✅ | hecho 2026-06-01. *Filtros avanzados/conversaciones: pendiente* |
| F8 | **Vista "Leads calientes"** (destacar `lead_score` alto) | 🟢 | el dato ya se calcula |
| F9 | **Exportar a CSV** contactos/conversaciones desde el dashboard | 🟢 | |
| F10 | **Toggle tema claro/oscuro** | 🟢 | el theming ya existe |
| F11 | **Notas internas** en una conversación (solo el equipo) | 🟢 | |
| F12 | **Etiquetas/tags** personalizadas por contacto | 🟢 | además del lead_score |
| F13 | **Command palette (Ctrl/Cmd+K)** para navegar rápido | 🟢 | |
| F14 | **Historial de cambios** de la config del agente | 🟢 | |
| F15 | **Mensaje de bienvenida automático** configurable al primer contacto | 🟢 | |
| F16 | **Respuestas rápidas / plantillas** en la bandeja (para el takeover humano) | 🟡 | takeover ya existe |
| F17 | **Editor visual de FAQs** (agregar/quitar/reordenar) | 🟡 | hoy es texto plano |
| F18 | **Ver el "cerebro" del agente** (prompt final) | 🟢 ⚙️ | endpoint `/agent/config/preview` ya existe |
| F19 | **Configurar horario de atención** con UI | 🟡 | business hours ya se usan en llamadas |
| F20 | **Página "Mi plan y uso"** (consumo del mes vs límite, barra de progreso) | 🟡 | |
| F21 | **Perfil de contacto enriquecido** (historial, notas, etiquetas) | 🟡 | |
| F22 | **Gráficos en el dashboard** (tendencia de mensajes, embudo de leads) | 🟡 | recharts ya instalado |
| F23 | **Responsive / PWA móvil** para gestionar desde el celular | 🟡 | |
| F24 | **Simulador de llamada de voz de prueba** | 🟡 🔑 ⚙️ | endpoint `/agent/voice/test-call` ya existe |
| F25 | **Inbox tipo helpdesk**: asignar conversación a un miembro, resolver, snooze | 🟡 | |
| F26 | **Acciones en lote** en Contactos (exportar/etiquetar/no-contactar varios) | 🟡 | |
| F27 | **Calendario de citas** | 🟡 | el agente ya detecta `appointment_date` |
| F28 | **Modo "fuera de oficina"** con mensaje automático | 🟡 | |
| F29 | **Tour guiado** la primera vez (tooltips paso a paso) | 🟡 | |
| F30 | **Widget de chat web embebible** para la página del cliente (otro canal) | 🔴 | |

## 2. Frontend — Super Admin (tú)

| # | Idea | Esf. | Notas |
|---|---|---|---|
| A1 | **Buscar clientes** (por nombre/slug) | ✅ | hecho 2026-06-01. *Ordenar por uso/fecha: pendiente* |
| A2 | **Detalle de un cliente** (drill-down: conversaciones, uso, ingreso) | 🟢/✅ | parcial 2026-06-01: la tabla ya muestra msgs/llamadas/Claude $/ingreso/ganancia por negocio |
| A3 | **Métricas con gráficos** (MRR, ganancia, actividad mensual, ingreso por plan) | ✅ | hecho 2026-06-01 (`GET /admin/analytics` + dashboard) |
| A7 | **Super Admin solo-administración** (ocultar módulos de negocio) | ✅ | hecho 2026-06-01 |
| A4 | **Gestión del equipo del cliente** (invitar usuarios admin/agent) | 🟡 | roles ya existen en el enum |
| A5 | **Visor de logs de webhooks por cliente** | ✅ | hecho 2026-06-01: botón 📜 por fila → modal (`GET /admin/tenants/{id}/webhooks`) |
| A6 | **Impersonar cliente** (entrar como el dueño para soporte) | 🔴 | potente, cuidar seguridad |

## 3. Backend — Funcionalidad

| # | Idea | Esf. | Notas |
|---|---|---|---|
| B1 | **Anti-spam por contacto** (throttle de respuestas) | 🟢 | ahorra tokens |
| B2 | **Reset mensual automático** de contadores (cron día 1) | 🟡 | hoy es manual |
| B3 | **Aviso al dueño** cuando hay lead caliente o escalamiento | 🟡 🔑 | |
| B4 | **Resumen automático de chats** | 🟡 🔑 ⚙️ | `call_summarizer` ya existe para llamadas; replicar para WhatsApp |
| B5 | **Auto-llamada al lead caliente** (si score > X) | 🟡 🔑 | `call_lead` ya existe |
| B6 | **Diferenciar roles** owner/admin/agent | 🟡 | el enum existe, casi nadie lo aplica |
| B7 | **Soft-delete / papelera de clientes** (30 días) | 🟡 | en vez de borrado duro |
| B8 | **Feature flags por plan** (ej. voz solo en Professional+) | 🟡 | |
| B9 | **Límites configurables por cliente** (override de los del plan) | 🟡 | |
| B10 | **Cron "tu prueba vence pronto"** (aviso a 3 días y al vencer) | 🟡 🔑 | |
| B11 | **Programar mensajes** + **broadcasts segmentados** por etapa de lead | 🟡 🔑 | |
| B12 | **Detección de sentimiento** del contacto (😡/😐/😊) | 🟡 🔑 | priorizar atención |
| B13 | **Cola de moderación de Instagram** (aprobar/rechazar antes de publicar) | 🟡 🔑 | |
| B14 | **Cache de respuestas frecuentes** (ahorrar tokens de Claude) | 🟡 🔑 | |
| B15 | **Plantillas de WhatsApp (HSM)** para mensajes proactivos/reactivación | 🟡 🔑 | Meta las exige fuera de 24h |
| B16 | **Reporte semanal por WhatsApp al dueño** | 🟡 🔑 | la automation `weekly_report` está definida; verificar que corra |
| B17 | **Agendamiento real de citas** / Google Calendar | 🔴 🔑 | el agente ya detecta `appointment_date` |
| B18 | **Base de conocimiento (RAG)** — subir catálogo/PDF para que el agente responda con eso | 🔴 🔑 | mucho más útil que solo FAQs |
| B19 | **Más canales**: Telegram / Messenger | 🔴 | la arquitectura de webhooks ya es por canal |
| B20 | **API pública por cliente** (API key propia) + **webhook saliente** | 🔴 | para que conecte su CRM/sistema |

## 4. Backend — Seguridad y robustez (antes de cobrar/escalar)

| # | Idea | Esf. | Notas |
|---|---|---|---|
| S1 | **Rate limit + bloqueo en login** (anti fuerza bruta) | 🟢 | |
| S2 | **CAPTCHA en el registro** público | 🟢 | anti-bots |
| S3 | **Revocación de tokens / logout real** | 🟡 | hoy el JWT es stateless |
| S4 | **Auditoría del panel admin** (quién creó/borró/cambió plan) | 🟡 | |
| S5 | **Backups automáticos de Postgres** + restauración probada | 🟡 | |
| S6 | **Webhook de WhatsApp: rechazar sin `META_APP_SECRET`** en producción | ✅ | hecho 2026-06-01 (verificado en runtime) |
| S7 | **Monitoreo de errores (Sentry)** + health checks de DB/Redis/colas | 🟡 | |
| S8 | **Security headers** (CSP, HSTS) + **request-id** de correlación en logs | 🟡 | |
| S9 | **Derecho al olvido por contacto** (borrar UNA persona, no todo el cliente) | 🟡 | legal |
| S10 | **2FA para tu cuenta de Super Admin** | 🟡 | |
| S11 | **Rotación de secretos** y cifrado de más PII en reposo | 🟡 | |
| S12 | **Aislamiento entre clientes forzado** | ✅/🔴 | hecho 2026-06-01 a nivel de capa de datos (`tenant_scope.py`, imposible olvidar el filtro). *Falta capa extra:* RLS **nativo** de Postgres (rol restringido) en el despliegue de producción |

## 5. Crecimiento / negocio / retención

| # | Idea | Esf. | Notas |
|---|---|---|---|
| G1 | **Centro de ayuda / videos de onboarding** dentro del dashboard | 🟢 | |
| G2 | **Programa de referidos** (código por cliente → descuento) | 🟡 | |
| G3 | **Cupones/descuentos** al crear negocio | 🟡 | |
| G4 | **Plantillas de negocio por rubro** pre-armadas (tono, servicios, ejemplos) | 🟡 | agente listo en 1 clic |
| G5 | **Panel de NPS / feedback** del cliente | 🟡 | medir satisfacción |
| G6 | **Cobro recurrente con Culqi** (webhook de renovación) + historial de facturas | 🔴 🔑 | |

---

## Cómo se relaciona con el plan por fases

- La columna ⭐ y la sección "Recomendado" = **Fase 0** (pulido sin keys) de `PLAN_MAESTRO.md`.
- Las 🔑 entran cuando actives la key correspondiente (Fases 1–4).
- Las de seguridad (sección 4) son **previas a cobrar a terceros**.

Ver el plan completo en `docs/PLAN_MAESTRO.md`.
