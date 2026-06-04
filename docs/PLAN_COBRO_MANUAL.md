# Módulo de cobro manual (sin Culqi) + notificaciones

> **Estado:** ✅ IMPLEMENTADO (2026-06-02). Notificaciones V1 visual (panel + banner).
> **Objetivo:** cobrar mensual por adelantado vía Yape/transferencia (sin comisión de
> Culqi), con avisos al negocio y al super admin, y desactivación automática si no paga.
> Culqi queda **dormido en el código** (degrada solo si no hay keys), listo para activar
> en el futuro sin reescribir nada.

## ✅ Qué quedó implementado

**Backend** (56 tests pasando, +5 nuevos en `tests/test_billing_integration.py`):
- `Tenant`: columnas `next_payment_due`, `last_payment_at`, `monthly_amount_pen`,
  `billing_suspended` + propiedades `payment_state` / `payment_due_at` / `service_blocked`
  (migración `004_manual_billing`).
- Excepción `PaymentOverdueError` (402 `PAYMENT_OVERDUE`); `get_current_tenant` bloquea a
  los suspendidos; el agente WhatsApp y las llamadas salientes dejan de operar (`service_blocked`).
- Endpoints (superadmin): `GET /admin/billing/pending`, `POST /admin/tenants/{id}/confirm-payment`
  (mueve el vencimiento +1 mes y reactiva; trial→basic), `POST /admin/tenants/{id}/suspend-billing`.
- Público: `GET /tenants/payment-info` (datos de Yape/transferencia desde `PAYMENT_*` en `.env`).

**Frontend** (`npm run build` ✅):
- Panel del fundador: sección **"Cobros por revisar"** con [Marcar pagado] / [Suspender].
- `TrialBanner`: avisa también el vencimiento de la mensualidad (por vencer / vencido).
- `UpgradePage`: muestra tus datos de Yape/transferencia (lee `/tenants/payment-info`).
- Interceptor: redirige a `/app/upgrade` también ante `402 PAYMENT_OVERDUE`.

**Config:** `PAYMENT_YAPE_NUMBER`, `PAYMENT_ACCOUNT_HOLDER`, `PAYMENT_BANK_ACCOUNT`,
`PAYMENT_CONTACT_WHATSAPP`, `PAYMENT_NOTE` (en `.env.example` y `.env.production`).

> Pendiente opcional (V2/V3): emails automáticos (Resend) y aviso por WhatsApp. La
> notificación hoy es **visual** (badge en el panel + banner en el dashboard).

---

## Plan original (referencia)

---

## 0. Resumen del flujo deseado

```
Registro → 14 días TRIAL gratis (ya existe, ya expira y bloquea solo)
   │
   ├─ Faltan ≤3 días → aviso al NEGOCIO: "se acerca tu fecha de pago"  [NUEVO]
   │
Vence el periodo
   │
   ├─ Aviso al SUPER ADMIN: "venció [Negocio]. ¿Pagó? [Sí] [No]"        [NUEVO]
   │
   ├─ Marcas SÍ → suma 1 mes a la fecha de pago, sigue activo           [NUEVO]
   └─ Marcas NO → se desactiva la plataforma del negocio                [reusa lo existente]
```

El negocio te paga **por su cuenta** (Yape/Plin/transferencia/depósito). El sistema
**no procesa el dinero**; solo lleva el control de fechas, te avisa y habilita/deshabilita.

---

## 1. Lo que YA existe (se reutiliza, no se toca)

- **Trial de 14 días que expira y bloquea** (`Tenant.is_trial_expired`, HTTP 402 →
  `/app/upgrade`). — `backend/app/dependencies.py`, `backend/app/models/tenant.py`.
- **Activar/desactivar negocio** (`Tenant.is_active`) desde el panel admin. — endpoint
  admin + botón en `frontend/src/pages/admin/AdminPage.tsx`.
- **Cambiar de plan** manualmente desde el panel admin.
- **Sección "Solicitudes de recuperación"** en el panel admin → es el **patrón exacto**
  a copiar para la nueva sección de "Cobros por revisar" (lista + botones de acción).
- **Culqi degrada solo** si no hay `CULQI_SECRET_KEY` (no hay que borrar nada).

## 2. Lo que FALTA (cambios nuevos, pequeños y aislados)

### 2.1 Base de datos (1 migración Alembic)
Agregar al modelo `Tenant` (o a `Subscription`, recomendado en `Tenant` por simplicidad):

| Campo | Tipo | Para qué |
|---|---|---|
| `billing_cycle_start` | datetime, nullable | inicio del periodo pagado actual |
| `next_payment_due` | datetime, nullable | fecha en que vence el próximo pago |
| `last_payment_at` | datetime, nullable | último pago confirmado |
| `billing_status` | enum: `trial` / `active` / `due_soon` / `overdue` / `suspended` | estado de cobro (derivable, pero guardarlo simplifica el panel) |
| `monthly_amount_pen` | int | monto mensual acordado (S/149 / 249 / 449 / 799 o personalizado) |

> Alternativa sin migración fuerte: reutilizar `Subscription.current_period_end` como
> `next_payment_due` y `Subscription.status` (`active`/`past_due`). Decидir al implementar.

### 2.2 Backend — lógica
1. **Al terminar el trial / al activar plan pagado:** setear `next_payment_due = hoy + 1 mes`
   y `billing_status = active`.
2. **Tarea programada diaria** (ya hay infra de cron con Modal/Celery):
   - Si `next_payment_due - hoy <= 3 días` y status `active` → marcar `due_soon`
     (dispara aviso al negocio).
   - Si `hoy >= next_payment_due` → marcar `overdue` (dispara aviso al super admin).
3. **Endpoints nuevos (panel super admin, protegidos por `AdminGuard`):**
   - `GET /admin/billing/pending` → lista de negocios `overdue`/`due_soon` (nombre, plan,
     monto, días de atraso).
   - `POST /admin/billing/{tenant_id}/confirm-payment` → marca pago: `last_payment_at = hoy`,
     `next_payment_due += 1 mes`, `billing_status = active`. (El "Sí".)
   - `POST /admin/billing/{tenant_id}/suspend` → `is_active = false`, `billing_status = suspended`.
     (El "No"; reusa el desactivar existente.)
   - `POST /admin/billing/{tenant_id}/reactivate` → reactiva tras pago tardío.
4. **Enforcement:** cuando `billing_status = suspended` (o `is_active = false`), el negocio
   queda bloqueado igual que un trial vencido (redirige a `/app/upgrade`). Se reaprovecha
   el mecanismo del 402.

### 2.3 Frontend
1. **Panel Super Admin** (`AdminPage.tsx`): nueva sección **"Cobros por revisar"** —
   tabla con negocios vencidos/por vencer y botones **[Marcar pagado]** / **[Suspender]**.
   Copiar el patrón visual de la sección "Solicitudes de recuperación".
2. **Dashboard del negocio:** banner de aviso cuando `billing_status = due_soon`
   ("Tu pago vence el DD/MM. Paga por Yape al 999... para no perder el servicio.").
   Reusar el componente `TrialBanner` existente.
3. **Pantalla `/app/upgrade`:** mostrar tus datos de pago (Yape/Plin/cuenta) en vez de
   (o además de) el botón de Culqi.

### 2.4 Notificaciones (cómo se "avisa")
Orden de menor a mayor esfuerzo — empezar por lo simple:
- **V1 (mínimo viable):** los avisos son **visuales en los paneles** (badge/contador en
  el panel admin = "3 cobros por revisar"; banner en el dashboard del negocio). Cero
  costo, cero dependencias. **Recomendado para arrancar.**
- **V2:** email automático (ya existe `notification_service` + Resend) al negocio cuando
  entra en `due_soon`, y a ti cuando un negocio entra en `overdue`.
- **V3 (futuro):** mensaje por WhatsApp al negocio (reusa el canal ya integrado).

## 3. Sobre Culqi (respuesta a tu duda)

- **No hay que modificar ni borrar Culqi.** Si no pones `CULQI_SECRET_KEY`, el servicio
  (`services/culqi_service.py`) y el webhook (`webhooks/culqi.py`) simplemente no se
  ejecutan. Queda inerte.
- El día que quieras cobros automáticos con tarjeta, activas las keys y el flujo manual
  y el automático pueden coexistir (unos pagan por Yape, otros con tarjeta).
- **Ahorro:** cobrando por Yape/transferencia te quedas con el 100% (Culqi cobra ~3.99% +
  IGV por transacción).

## 4. Estimación y orden de trabajo

| Paso | Esfuerzo | Riesgo |
|---|---|---|
| Migración + campos en `Tenant` | bajo | bajo |
| Lógica de fechas + tarea diaria | bajo-medio | bajo |
| Endpoints admin de cobro | bajo | bajo |
| Sección "Cobros por revisar" (frontend) | medio | bajo |
| Banner de aviso al negocio | bajo | bajo |
| `/app/upgrade` con datos de Yape | bajo | bajo |
| (V2) emails automáticos | bajo | bajo |

**No rompe nada de lo ya construido.** Todo es aditivo y reutiliza el bloqueo del trial,
el activar/desactivar y el patrón de la sección de recuperación de contraseñas.

## 5. Decisiones pendientes (para confirmar antes de codear)

1. ¿Guardar los campos de cobro en `Tenant` (simple) o en `Subscription` (más "correcto")?
2. ¿Notificación V1 (solo visual) para arrancar, o directamente V2 (emails)?
3. ¿Mostrar tus datos de Yape/cuenta en `/app/upgrade` (configurable desde el panel)?
4. ¿El monto mensual se fija por plan (149/249/449/799) o permites monto personalizado por negocio?
