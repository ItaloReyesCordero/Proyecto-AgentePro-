# 📋 Plan de Mejoras AgentePro — "de bueno a revolucionario"

> Plan de evolución del producto (backend + frontend), ordenado por fases de
> ejecución, con esfuerzo estimado. Cada fase deja algo usable y desplegable.
> Estimación base: 1 desarrollador full-time. **Total: ~9 a 12 semanas.**

---

## ✂️ Ideas descartadas (poco impacto o demasiado comunes)

- **Caché simple de respuestas** → se absorbe dentro del RAG, no como feature aparte.
- **Command palette (⌘K)** → queda como detalle de pulido, no como hito.
- **Health check básico** → se sube de nivel a observabilidad real (Fase 0).

---

## FASE 0 — Cimientos y confianza (~1 semana)

*Antes de construir lo grande. Sin esto, lo demás se cae en producción.*

| # | Qué | Por qué resalta | Esfuerzo |
|---|-----|-----------------|----------|
| B0.1 | **Idempotencia en webhooks** (Twilio/Instagram: dedup por `message_id` en Redis) | Evita respuestas y cobros duplicados | 1 día |
| B0.2 | **Cola con dead-letter + reintentos** en Celery (`worker`) | Ningún lead se pierde si falla una tarea | 2 días |
| B0.3 | **Observabilidad**: logging estructurado con `trace_id` por conversación + `/health/deep` (Postgres, Redis, Twilio, Claude, Retell) | Detectas caídas antes que el cliente | 2 días |
| F0.1 | **Estados vacíos, error y skeletons** consistentes en todas las páginas | Producto se siente premium y rápido | 2 días |

**Entregable:** sistema confiable y monitoreable.

---

## FASE 1 — Sistema de diseño UX/UI (~1.5 semanas)

*El "wow" visual. Un producto bonito vende y retiene.*

| # | Qué | Detalle |
|---|-----|---------|
| F1.1 | **Design system real**: tokens de color (violeta/fucsia), tipografía, espaciados, sombras, radios — en `theme.ts` + Tailwind config | Consistencia total |
| F1.2 | **Dark mode pulido** (sobre `AppearanceSettings`) | Contrastes correctos, sin colores rotos |
| F1.3 | **Micro-interacciones** con Framer Motion: transiciones de página, hover, entrada de mensajes, feedback al guardar | Fluidez tipo Linear/Notion |
| F1.4 | **Layout responsivo + base PWA** (instalable en el celular del dueño) | Gestión desde el móvil |
| F1.5 | **Accesibilidad (a11y)**: focus visible, navegación por teclado, ARIA, contraste AA | Profesionalismo + más usuarios |

**Entregable:** identidad visual coherente y moderna en toda la app.

---

## FASE 2 — Inteligencia del agente (~2-3 semanas)

*El corazón revolucionario.*

| # | Qué | Por qué es el diferenciador | Esfuerzo |
|---|-----|------------------------------|----------|
| B2.1 | **RAG / base de conocimiento por negocio** (pgvector): el tenant sube catálogo/PDFs/FAQs → embeddings → el agente responde con SU info real, sin alucinar | Convierte un bot genérico en experto del negocio. Difícil de copiar | 1.5 sem |
| B2.2 | **Lead scoring en tiempo real** (sobre `lead_scorer` + `intent_detector`): score 0-100 actualizado por mensaje | Los vendedores atacan primero al lead caliente | 3-4 días |
| B2.3 | **Análisis de sentimiento + alerta de fricción** (cliente molesto → escalar) | Salvas ventas antes de perderlas | 2-3 días |

**Entregable:** un agente que sabe del negocio y prioriza solo.

---

## FASE 3 — Experiencia operativa del usuario (~2-3 semanas)

*Donde el dueño vive a diario.*

| # | Qué | Por qué resalta | Esfuerzo |
|---|-----|-----------------|----------|
| F3.1 | **Bandeja unificada omnicanal** (WhatsApp + Instagram + llamadas en un inbox estilo Intercom, con score e historial del lead al lado) | El usuario deja de saltar entre apps. Brutal para retención | 1.5-2 sem |
| F3.2 + B3.1 | **Notificaciones en tiempo real** (sobre `socket.ts`): toast + badge + sonido cuando entra lead caliente | Nadie pierde un lead | 3 días |
| F3.3 + B3.2 | **Takeover humano en vivo** (mejora "pasar con el dueño"): el dueño toma el control de la conversación desde el inbox y la IA cede | Combina IA + humano sin fricción | 4-5 días |

**Entregable:** centro de operaciones omnicanal en tiempo real.

---

## FASE 4 — Autosuficiencia y métricas (~2-3 semanas)

*Máximo impacto comercial.*

| # | Qué | Por qué es el mayor diferenciador | Esfuerzo |
|---|-----|-----------------------------------|----------|
| F4.1 + B4.1 | **Constructor de agente no-code + playground en vivo** (sobre `agent/` y `test_message`): el dueño configura personalidad, reglas y conocimiento, lo prueba en un chat real y publica | El cliente siente el agente 100% suyo → autosuficiente. Top impacto de venta | 2-3 sem |
| F4.2 + B4.2 | **Motor de automatizaciones proactivo** (sobre `automations` + `follow_up_leads`): "si no responde en 24h → la IA redacta y manda follow-up". Reglas visuales | Ventas en piloto automático. Difícil de copiar | 1.5-2 sem |
| F4.3 + B4.3 | **Dashboard de ROI** + **analítica de costos/uso por tenant** (tokens, costo por canal, embudo) | El dueño VE el retorno → renueva. Tú ves tus márgenes | 1 sem |

**Entregable:** plataforma autoservicio que demuestra su propio ROI.

---

## 🗓️ Resumen de orden y tiempos

| Fase | Foco | Duración |
|------|------|----------|
| **0** | Confiabilidad + observabilidad | ~1 semana |
| **1** | Sistema de diseño UX/UI | ~1.5 semanas |
| **2** | Inteligencia del agente (RAG) | ~2-3 semanas |
| **3** | Inbox omnicanal + tiempo real | ~2-3 semanas |
| **4** | Constructor no-code + automatización + ROI | ~2-3 semanas |

**Total estimado: ~9 a 12 semanas** (1 desarrollador full-time).

### Por qué este orden
1. **Fase 0 primero** o lo grande se rompe en producción.
2. **Diseño (Fase 1) temprano** para que todo lo nuevo nazca ya bonito y consistente.
3. **RAG (Fase 2)** antes del inbox y el constructor, porque ambos dependen del agente inteligente.
4. **Constructor no-code al final**, porque consume todo lo anterior (diseño + RAG + automatización).
