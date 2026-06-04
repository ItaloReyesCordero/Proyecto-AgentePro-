# 📚 Documentación de AgentePro 2.0

Bienvenido. Esta carpeta explica **todo** el sistema: qué es, cómo funciona por dentro, cómo se relacionan las piezas, cómo probarlo y cómo operarlo. Está pensada para que lo entiendas de cero, aunque todavía no tengas ninguna API key configurada.

> **Estado actual:** el sistema corre completo en local con `docker compose` (backend, frontend, PostgreSQL, Redis, worker). Las integraciones externas (Claude, WhatsApp, Twilio, etc.) están **desactivadas con gracia** hasta que agregues sus claves: la app no se rompe, solo usa respuestas de respaldo.

---

## 🗺️ Índice de la documentación

| # | Documento | Qué responde |
|---|-----------|--------------|
| 00 | **Este README** | Mapa general y por dónde empezar |
| 01 | [Visión y conceptos](01-vision-y-conceptos.md) | Qué es el producto, para quién, qué hace cada módulo |
| 02 | [Arquitectura](02-arquitectura.md) | Diagrama del sistema, componentes, stack, cómo se comunican |
| 03 | [Modelo de datos](03-modelo-de-datos.md) | Tablas, relaciones, diagrama entidad-relación |
| 04 | [Flujos clave](04-flujos-clave.md) | Diagramas de secuencia: WhatsApp, voz, provisioning, Instagram |
| 05 | [Referencia de la API](05-api-referencia.md) | Todos los endpoints REST y webhooks |
| 06 | [Cuentas, roles y super admin](06-cuentas-roles-y-superadmin.md) | **Cuál es tu cuenta de super admin**, roles, login, JWT |
| 07 | [Guía de pruebas](07-guia-de-pruebas.md) | **Qué probar ahora (sin keys) y después (con keys)**, paso a paso |
| 08 | [Integraciones externas](08-integraciones-externas.md) | Cada servicio, su clave, qué pasa si falta |
| 09 | [Frontend / Dashboard](09-frontend-dashboard.md) | Páginas, diseño, cómo habla con el backend |
| 10 | [Operación y despliegue](10-operacion-y-despliegue.md) | Docker, migraciones, workers, Modal, Railway/Vercel |
| 11 | [🚀 Roadmap a producción](11-roadmap-a-produccion.md) | **TODO lo que falta + costos detallados**, paso a paso, en orden |

---

## ⚡ Resumen en 60 segundos

**AgentePro 2.0** es una plataforma **SaaS multi-tenant**: un mismo sistema atiende a muchos negocios ("tenants") a la vez, cada uno con sus datos aislados. Cuando un negocio paga, se le **auto-configura** todo: un agente de WhatsApp con IA, un agente de voz, un CRM (HubSpot), automatizaciones, generación de posts de Instagram y un dashboard.

```
Cliente final  ─(WhatsApp/Instagram/Llamada)─►  AgentePro  ─►  Claude (IA) responde
                                                    │
                                                    ├─► Guarda todo en la base de datos
                                                    ├─► Sincroniza con HubSpot (CRM)
                                                    └─► El dueño del negocio lo ve en su Dashboard en tiempo real
```

- **Backend:** FastAPI + Socket.io (Python 3.13) — `agentepro/backend`
- **Frontend:** React 19 + Vite + TypeScript — `agentepro/frontend`
- **Datos:** PostgreSQL + Redis
- **IA:** Claude (Anthropic)

---

## 🚀 Por dónde empezar a leer

1. Lee **[01 - Visión y conceptos](01-vision-y-conceptos.md)** para entender el "qué" y el "para qué".
2. Sigue con **[02 - Arquitectura](02-arquitectura.md)** para ver el "cómo".
3. Cuando quieras tocar el sistema, ve a **[07 - Guía de pruebas](07-guia-de-pruebas.md)**.
4. Para entender tu acceso de administrador, **[06 - Cuentas y super admin](06-cuentas-roles-y-superadmin.md)**.

> Los diagramas usan **Mermaid**: se ven como dibujos en GitHub/VS Code (con extensión de Mermaid) y como texto en cualquier editor.
