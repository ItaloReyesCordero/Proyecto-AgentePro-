# 05 · Referencia de la API

Base URL local: `http://localhost:8000`. Documentación interactiva (Swagger): **http://localhost:8000/docs** (activa porque `DEBUG=true`).

- Endpoints **privados**: requieren header `Authorization: Bearer <access_token>`.
- Endpoints **de plataforma** (`/admin/*`, `/provision`): requieren header `X-Admin-Key: <ADMIN_SECRET_KEY>`.
- Webhooks: públicos pero validados por firma/token.

---

## Salud
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |

## Autenticación — `/api/v1/auth`
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/auth/register` | — | Crea tenant + usuario dueño. Devuelve tokens |
| POST | `/auth/login` | — | Login. Devuelve `access_token`, `refresh_token`, `user` |
| POST | `/auth/refresh` | — | Renueva el access token con el refresh token |
| POST | `/auth/logout` | Bearer | Cierra sesión (el cliente descarta tokens) |
| GET | `/auth/me` | Bearer | Datos del usuario autenticado |

## Tenant / Suscripción
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/tenants/me` | Bearer | Datos del negocio del usuario |
| GET | `/subscriptions/me` | Bearer | Suscripción actual |

## Conversaciones — `/api/v1/conversations`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/conversations` | Lista paginada (filtros: `status`, `channel`, `page`, `per_page`) |
| GET | `/conversations/{id}` | Detalle |
| GET | `/conversations/{id}/messages` | Mensajes paginados |
| POST | `/conversations/{id}/messages` | Enviar mensaje manual (humano) |
| POST | `/conversations/{id}/takeover` | Tomar control humano |
| POST | `/conversations/{id}/release` | Devolver a la IA |
| POST | `/conversations/{id}/pause-bot` | Pausar el bot |
| POST | `/conversations/{id}/close` | Cerrar conversación |
| PATCH | `/conversations/{id}` | Actualizar tags / lead_stage |

## Contactos — `/api/v1/contacts`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/contacts` | Lista (filtros: `search`, `lead_stage`, paginación) |
| GET | `/contacts/{id}` | Detalle |
| PATCH | `/contacts/{id}` | Editar nombre, email, tags, etapa, notas |
| GET | `/contacts/{id}/conversations` | Conversaciones del contacto |
| GET | `/contacts/{id}/calls` | Llamadas del contacto |
| POST | `/contacts/{id}/do-not-contact` | Marcar "no contactar" |
| POST | `/contacts/{id}/call` | Llamar ahora (saliente) |
| POST | `/contacts/{id}/send-whatsapp` | Enviar WhatsApp manual |

## Llamadas — `/api/v1/calls`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/calls` | Lista (filtro `direction`) |
| GET | `/calls/{id}` | Detalle + transcript + resumen |
| GET | `/calls/{id}/recording` | URL de grabación |
| GET | `/calls/{id}/summary` | Resumen IA |
| POST | `/calls/outbound` | Iniciar llamada saliente |

## Instagram — `/api/v1/instagram`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/instagram/posts` | Lista de posts |
| POST | `/instagram/posts/generate` | Generar posts con IA |
| GET | `/instagram/posts/{id}` | Detalle |
| POST | `/instagram/posts/{id}/approve` | Aprobar y programar |
| POST | `/instagram/posts/{id}/reject` | Rechazar |
| POST | `/instagram/posts/{id}/publish` | Publicar ya |
| DELETE | `/instagram/posts/{id}` | Eliminar |
| GET | `/instagram/connect-url` | URL OAuth para conectar Instagram |

## Automatizaciones — `/api/v1/automations`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/automations` | Lista con métricas |
| PATCH | `/automations/{id}` | Activar/desactivar/configurar |
| GET | `/automations/{id}/runs` | Historial de ejecuciones |
| POST | `/automations/{id}/run` | Ejecutar manualmente |

## Agente / Voz — `/api/v1/agent` y `/api/v1/voice`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/agent/config` | Configuración del agente de chat |
| PUT/PATCH | `/agent/config` | Actualizar configuración |
| POST | `/agent/config/test` | **Probar el agente con un mensaje** (sin guardar) |
| GET | `/agent/config/preview` | Ver el system prompt generado |
| GET/PUT | `/agent/voice` | Configuración de voz |
| POST | `/agent/voice/test-call` | Llamada de prueba |
| GET/PUT | `/voice/config` | (Alias directo de configuración de voz) |

## Métricas — `/api/v1/metrics`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/metrics/summary` | KPIs (filtro `period=7d/30d/90d`) |
| GET | `/metrics/message-volume` | Volumen por día |
| GET | `/metrics/leads-funnel` | Embudo de leads |
| GET | `/metrics/costs` | Costo estimado de APIs |

## Plataforma (super admin) — `/api/v1`  ·  header `X-Admin-Key`
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/provision` | **Alta completa de un tenant** (auto-provisioning) |
| GET | `/admin/tenants` | Todos los tenants |
| GET | `/admin/tenants/{id}` | Detalle de tenant |
| PATCH | `/admin/tenants/{id}` | Modificar plan/estado |
| POST | `/admin/tenants/{id}/deactivate` | Desactivar tenant |
| GET | `/admin/metrics/global` | Métricas globales del SaaS |
| GET | `/admin/costs/global` | Costos globales |
| GET | `/admin/health` | Estado de cada integración |

## Webhooks — `/webhooks`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/webhooks/whatsapp/{slug}` | Verificación de Meta (challenge) |
| POST | `/webhooks/whatsapp/{slug}` | Mensajes entrantes de WhatsApp |
| GET/POST | `/webhooks/instagram/{slug}` | Verificación / DMs de Instagram |
| POST | `/webhooks/retell/{slug}` | Eventos de llamadas (Retell) |
| POST | `/webhooks/twilio/voice/{slug}` | Llamada entrante (devuelve TwiML) |
| POST | `/webhooks/culqi` | Eventos de pagos |

## Tiempo real (Socket.io)
Eventos que el backend **emite** al dashboard (room por tenant): `new_message`, `agent_typing`, `agent_response`, `escalation_needed`, `new_call`, `call_ended`, `call_completed`, `lead_score_updated`, `instagram_post_ready`.

## Siguiente
➡️ [06 · Cuentas, roles y super admin](06-cuentas-roles-y-superadmin.md)
