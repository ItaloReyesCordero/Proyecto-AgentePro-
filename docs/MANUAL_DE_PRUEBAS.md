# Manual de pruebas manuales — AgentePro 2.0

> Guía para que **tú (Italo)** verifiques a mano que TODO funciona antes y después del
> despliegue a producción. Marca cada casilla `[ ]` → `[x]` a medida que lo pruebas.
> Última actualización: 2026-06-02.

---

## 0. Antes de empezar

**Cuentas de prueba (entorno local / dev):**

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Super admin (tú) | `italoreyescordero1@gmail.com` | `SuperAdmin2026` |
| Dueño demo | `demo-trial@example.com` | `DemoTrial123` |

> ⚠️ En **producción** la contraseña del super admin es la de `backend/.env.production`
> (`SUPERADMIN_PASSWORD`). La contraseña dev NO cambia una cuenta ya creada.

**Cómo levantar la app en local:**
```
cd agentepro
docker compose up -d
```
- Frontend: http://localhost:5173
- Backend (API): http://localhost:8000  ·  Docs API: http://localhost:8000/docs

**Si cambiaste código del frontend y no se ve:** `docker compose restart frontend` y luego
`Ctrl+Shift+R` en el navegador (el watcher de Vite a veces no detecta cambios por el bind-mount).

---

## 1. Panel del Super Admin (tu panel de fundador)

Entra a http://localhost:5173 → inicia sesión con tu cuenta de super admin → menú **Admin**.
Verás **5 módulos en pestañas** arriba: Dashboard · Negocios · Uso y consumo · Cobros · Recuperación.

### 1.1 Módulo Dashboard
- [ ] Se ven 6 tarjetas (KPIs): Ingreso mensual (MRR), Ganancia est./mes, Clientes de pago, En prueba, Costo Claude, Mensajes totales.
- [ ] Se ve el gráfico "Actividad por mes" (mensajes y llamadas).
- [ ] Se ve el gráfico "Ingreso por plan".
- [ ] Se ve "Estado de servicios" con chips: cada API key sale con ✓ (configurada) o — (falta).
- [ ] Ningún número sale como "NaN" ni la página se queda en blanco.

### 1.2 Módulo Negocios  ⭐ (aquí está el botón que fallaba)
- [ ] La tabla lista todos los negocios con: Nombre, Plan, Estado (Activo/Inactivo), Acciones.
- [ ] **Cambiar plan:** cambia el `select` de plan de un negocio → aparece aviso "Negocio actualizado".
- [ ] **Desactivar negocio (prueba clave):**
  1. Pulsa **Desactivar** en el negocio demo → confirma el diálogo.
  2. El estado pasa a **Inactivo** (badge rojo) y sale el aviso "Negocio desactivado…".
  3. En **otra ventana/incógnito**, inicia sesión como el dueño demo (`demo-trial@example.com`).
  4. ✅ Debe redirigirte a la pantalla **"Tu servicio está en pausa"** (NO debe dejarte entrar al panel).
- [ ] **Reactivar negocio:**
  1. Vuelve al panel admin → pulsa **Activar** en ese negocio.
  2. El dueño demo, al recargar, ya puede entrar normalmente a su panel.
- [ ] **Crear negocio:** botón "Crear negocio" → llena el formulario → "Crear" → aparece en la lista.
- [ ] **Restablecer contraseña del dueño** (ícono llave): confirma → aparece un modal con la contraseña nueva (cópiala).
- [ ] **Ver logs de webhooks** (ícono lista): abre un modal (estará vacío si aún no hay WhatsApp conectado).
- [ ] **Exportar datos** (ícono descarga): descarga un `.json` con los datos del negocio.
- [ ] **Eliminar negocio** (ícono basura rojo): confirma → desaparece de la lista. ⚠️ Irreversible — prueba solo con un negocio de juguete.
- [ ] **Reiniciar uso mensual:** pone en 0 los contadores de mensajes/llamadas de todos.

### 1.3 Módulo Uso y consumo  ⭐ (lo nuevo que pediste)
- [ ] 4 KPIs arriba: Mensajes totales, Llamadas totales, Costo Claude total, MRR.
- [ ] Tabla por negocio con: Contactos, Mensajes, Llamadas, Tokens, **Claude $**, Ingreso, Ganancia.
- [ ] La tabla está ordenada por costo de Claude (mayor primero).
- [ ] Hay una fila de **Totales** al final que suma todo.
- [ ] Los negocios inactivos salen marcados con la etiqueta "inactivo".

### 1.4 Módulo Cobros (cobro manual por Yape)
- [ ] Muestra negocios "por vencer", "vencidos" o "suspendidos". Si no hay, dice "No hay cobros pendientes 🎉".
- [ ] La pestaña muestra un número (badge) con cuántos hay por revisar.
- [ ] **Marcar pagado:** mueve el vencimiento un mes y reactiva. Sale aviso de confirmación.
- [ ] **Suspender:** confirma → el negocio queda suspendido (su panel se bloquea, igual que en 1.2).

### 1.5 Módulo Recuperación (contraseñas olvidadas)
- [ ] Lista solicitudes de dueños que olvidaron su contraseña (badge con el número).
- [ ] **Restablecer contraseña:** genera una contraseña nueva en un modal (se muestra una sola vez).
- [ ] **Descartar:** quita la solicitud sin cambiar nada.

---

## 2. Flujo del Dueño de un negocio (cliente)

Inicia sesión con la cuenta del dueño demo (`demo-trial@example.com`).

### 2.1 Registro y onboarding
- [ ] Registro de un negocio nuevo desde `/register` crea una prueba de 14 días.
- [ ] El onboarding pide datos del negocio y (paso 2) conectar WhatsApp (puede saltarse sin keys).

### 2.2 Panel del dueño
- [ ] **Dashboard:** se ven métricas (mensajes, leads, etc.) sin errores.
- [ ] **Conversaciones:** la lista carga (vacía si no hay WhatsApp conectado).
- [ ] **Contactos / Leads:** la lista carga.
- [ ] **Agente (config):** puedo editar el prompt/personalidad y **Guardar** sin error 500.
- [ ] **Voz (config):** puedo abrir y guardar la configuración de voz.
- [ ] **Automatizaciones:** la lista carga y puedo activar/desactivar.
- [ ] **Instagram:** la sección de posts carga.
- [ ] **Ajustes:** puedo cambiar tema (claro/oscuro) y color de marca.
- [ ] **Llamadas:** la lista carga.

### 2.3 Banner de prueba / pago
- [ ] Con una prueba activa, se ve un banner con los días restantes.
- [ ] Cuando la prueba vence (o el admin suspende), al navegar te manda a **"Tu servicio está en pausa"** con los datos de Yape.

### 2.4 Recuperar contraseña
- [ ] En `/login` → "¿Olvidaste tu contraseña?" → ingresa el correo → mensaje genérico ("si existe, te contactaremos").
- [ ] Esa solicitud aparece en el módulo **Recuperación** del super admin (sección 1.5).

---

## 3. Verificación técnica rápida (opcional, por consola)

Desde `agentepro/`:
```
# Tests del backend (deben pasar todos)
docker compose exec backend python -m pytest -q

# ¿Qué API keys están configuradas? (todo en false = aún sin configurar)
curl -s http://localhost:8000/api/v1/admin/health -H "X-Admin-Key: <ADMIN_SECRET_KEY>"
```

---

## 4. Estado actual del sistema (verificado 2026-06-02)

### ✅ Lo que funciona
- Login super admin y dueño; aislamiento por negocio (multi-tenant).
- Panel admin con los 5 módulos (Dashboard, Negocios, Uso, Cobros, Recuperación).
- **Activar/Desactivar negocio**: ahora bloquea de verdad el panel del dueño (402 "cuenta suspendida")
  y detiene su agente de WhatsApp/Instagram y las llamadas. **Bug corregido.**
- Cobro manual (Yape): marcar pagado / suspender, banner y pantalla de pago.
- Recuperación de contraseñas (solicitud del dueño → aprobación del admin).
- Todos los endpoints de negocio (contactos, conversaciones, agente, voz, métricas, automatizaciones, Instagram, llamadas) responden 200.
- 517 pruebas automáticas del backend en verde.

### ⚠️ Lo que NO funcionará hasta configurar API keys (esperado)
> En `/admin` → Dashboard → "Estado de servicios" verás todo con "—". Eso significa que
> **falta poner las llaves**. Sin ellas:
- **`anthropic` (Claude)** → el agente **no puede responder** con IA. ⛔ Es la llave más importante.
- **`meta_whatsapp`** → no se reciben ni envían mensajes de WhatsApp/Instagram reales.
- **`twilio` + `retell`** → no funcionan las llamadas de voz.
- **`hubspot`** → no se sincroniza el CRM (opcional).
- **`resend`** → no se envían correos (opcional).
- **`fal`** → no se generan imágenes para Instagram (opcional).
- **`culqi`** → pasarela de pago (a propósito apagada; cobras por Yape).

👉 Cómo obtener cada llave: ver **`docs/COMO_CONSEGUIR_API_KEYS.md`**.

---

## 5. Checklist de despliegue a producción

- [ ] VPS + dominio + HTTPS (certificado SSL).
- [ ] Copiar `backend/.env.production` → `backend/.env` y rellenar los `<<< ... >>>`:
  - [ ] `DATABASE_URL` y `DATABASE_URL_SYNC` (Postgres de producción).
  - [ ] `REDIS_URL`.
  - [ ] `FRONTEND_URL` (tu dominio).
  - [ ] **`ANTHROPIC_API_KEY`** (imprescindible).
  - [ ] `META_*` (WhatsApp Cloud API) por cada cliente.
  - [ ] `SUPABASE_*` (backups off-site) — opcional pero recomendado.
- [ ] No rotar `SECRET_KEY` después de tener clientes (rompe el cifrado de tokens de WhatsApp/IG).
- [x] Política de privacidad + términos **YA CREADOS** en `/privacidad` y `/terminos` (Meta los exige). Solo falta que tengan URL pública real al desplegar el dominio (ej. `https://tudominio.com/privacidad`).
- [ ] RLS nativo de Postgres (recomendado para aislamiento a nivel BD).
- [ ] Levantar con `docker compose -f docker-compose.prod.yml up -d`.
- [ ] Probar TODO este manual otra vez ya en el servidor real (especialmente WhatsApp de punta a punta).
- [ ] Verificar que los backups (`agentepro/backups/`) se crean y se suben a Supabase.

---

## 6. Si algo falla

- **El panel del dueño no se bloquea al desactivar:** confirma que reiniciaste el backend
  (`docker compose restart backend`) y que el front está actualizado (`restart frontend` + `Ctrl+Shift+R`).
- **El agente no responde:** revisa que `anthropic` salga en ✓ en Estado de servicios.
- **Errores 500 al guardar config:** revisa logs con `docker compose logs backend --tail=50`.
- **No llegan mensajes de WhatsApp:** revisa el módulo Negocios → ícono "logs de webhooks" del negocio.
