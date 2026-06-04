# PRICING — AgentePro

Precios en soles peruanos (PEN). Costos de APIs estimados por cliente/mes (referenciales, varían con uso real y tipo de cambio). Decisión de precios del dueño (2026-06-04): **4 planes**, SIN "ilimitado" real (tope de uso justo para no perder dinero en negocios muy concurridos).

## Planes y precios de venta

| Plan | Precio venta (S/) | Mensajes WhatsApp | Llamadas voz | Módulos incluidos |
|---|---|---|---|---|
| **Inicial** | 149 | 200 | — | Dashboard, Conversaciones, Agente IA, Configuración |
| **Basic** | 249 | 400 | — | + Contactos (CRM) |
| **Professional** | 449 | 1,500 | 60 | + Instagram IA, Citas + recordatorios, Voz, Reporte semanal |
| **Enterprise** | 799 | 4,000 | 150 | + Automatizaciones / Reactivación, soporte prioritario |
| *Trial (14 días)* | 0 | 200 | 10 | Funciones de Professional con topes de prueba (cuenta desde el día 1) |

Los topes ya NO son "ilimitados": con la voz a ~S/1.50/llamada, un ilimitado real haría perder dinero. Los números viven en `backend/app/config.py` y `backend/.env` (`PLAN_*_MESSAGES`, `PLAN_*_CALLS`, `PLAN_*_PRICE`).

## Costo real de APIs por unidad (medido en pruebas)

| Recurso | Costo aprox. | Nota |
|---|---|---|
| 1 mensaje WhatsApp con IA (Claude + envío) | ~S/ 0.05 | Claude Sonnet, crece un poco con el historial |
| 1 llamada de voz (~3 min, Retell + Twilio) | ~S/ 1.50 | Es el costo dominante |
| Número WhatsApp/voz Twilio por negocio | ~S/ 4 – 8/mes | Solo planes con voz compran número |

## Costo estimado de APIs por cliente/mes (a uso máximo del plan)

| Componente | Inicial | Basic | Professional | Enterprise |
|---|---|---|---|---|
| Claude (mensajes IA) | ~S/ 10 | ~S/ 20 | ~S/ 60 | ~S/ 150 |
| Envío WhatsApp | ~S/ 4 | ~S/ 4 | ~S/ 15 | ~S/ 40 |
| Voz (Retell + Twilio) | — | — | ~S/ 90 | ~S/ 225 |
| Número Twilio | — | — | ~S/ 8 | ~S/ 10 |
| **Total costo** | **~S/ 14** | **~S/ 24** | **~S/ 173** | **~S/ 435** |
| **Ganancia** | **~S/ 135 (91%)** | **~S/ 225 (90%)** | **~S/ 276 (61%)** | **~S/ 365 (46%)** |

> Importante: estos costos los paga el dueño conectando UNA tarjeta con autorecarga + tope/alerta en Anthropic, Retell y Twilio. Se cubren con la mensualidad del cliente. Por eso los planes altos tienen tope de uso justo.

## Break-even

Con ganancia promedio ≈ **S/ 250/cliente** y costos fijos de infraestructura ≈ **S/ 80–120/mes** (Railway + dominio):

> **Break-even ≈ 1 cliente.**

> Las cifras son estimaciones de planificación; valida con el consumo real de cada API en `/api/v1/metrics/costs` y en el panel del fundador (`/admin/analytics`, columna "Costo real").
