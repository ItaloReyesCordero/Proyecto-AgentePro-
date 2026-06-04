# 07 · Guía de pruebas

Qué puedes probar **ahora mismo sin ninguna API key**, y qué necesitará claves más adelante.

## ✅ Lo que YA funciona sin keys (degradación con gracia)

| Funciona | Porque… |
|----------|---------|
| Login y dashboard completo | No depende de servicios externos |
| Verificación de webhook de WhatsApp | Solo compara el token del tenant |
| Recibir mensajes y crear contactos/conversaciones | Es lógica interna + DB |
| El agente "responde" | Sin Claude usa un **mensaje de respaldo** (pero el flujo completo corre) |
| Métricas, contactos, automatizaciones, posts (CRUD) | Todo es base de datos |
| Auto-provisioning de un tenant | Crea todo en DB; Twilio/Retell/HubSpot quedan en `null` |
| Endpoints de super admin | Solo dependen de `X-Admin-Key` |

## 🔑 Lo que necesita keys para verse "de verdad"

| Necesita | Para qué |
|----------|----------|
| `ANTHROPIC_API_KEY` | Que el agente dé respuestas reales de Claude (chat, resúmenes, posts) |
| Meta WhatsApp (`META_APP_*` + token del tenant) | Enviar/recibir WhatsApp real |
| Twilio + Retell | Llamadas de voz reales |
| HubSpot | Sincronización CRM real |
| fal.ai | Imágenes reales de Instagram |
| Culqi | Cobros reales |
| Resend | Emails de bienvenida reales |

---

## Parte 1 — Pruebas desde el navegador (recomendado)

1. Abre **http://localhost:5173**.
2. Inicia sesión: `dueno@clinicasonrisa.pe` / `secret123`.
3. Recorre el menú lateral:
   - **Dashboard:** KPIs y gráficos (con datos reales de la DB).
   - **Conversaciones:** verás la conversación de prueba ("Carlos Ruiz"). Abre el hilo: están el mensaje del cliente y la respuesta del agente. Prueba **"Tomar control"** y enviar un mensaje manual.
   - **Contactos:** pipeline tipo Kanban; mueve un contacto de etapa con el selector.
   - **Agente IA:** edita FAQs/servicios, **Guardar**, y usa el panel **"Probar agente"** (sin key, verás el mensaje de respaldo + metadatos).
   - **Llamadas / Instagram / Automatizaciones / Configuración:** explora; en *Configuración* verás la URL de tu webhook de WhatsApp.

## Parte 2 — Simular un mensaje de WhatsApp entrante (sin Meta)

Como el `META_APP_SECRET` está vacío en dev, puedes hacer el POST tú mismo:

```bash
SLUG="clinica-sonrisa-9fb671"   # tu slug real (míralo en Configuración o /tenants/me)

curl -X POST "http://localhost:8000/webhooks/whatsapp/$SLUG" \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{
        "contacts":[{"wa_id":"51977777777","profile":{"name":"María López"}}],
        "messages":[{"id":"wamid.DEMO2","from":"51977777777","type":"text",
                     "text":{"body":"Hola, ¿cuánto cuesta una limpieza dental?"}}]
      }}]}]}'
```

Luego abre **Conversaciones** en el dashboard: aparecerá el nuevo contacto y su hilo (con respuesta de respaldo). Con `ANTHROPIC_API_KEY` configurada, la respuesta sería de Claude.

## Parte 3 — Pruebas de super admin (cURL)

```bash
ADMIN="X-Admin-Key: dev-admin-key"

curl http://localhost:8000/api/v1/admin/tenants -H "$ADMIN"        # lista negocios
curl http://localhost:8000/api/v1/admin/metrics/global -H "$ADMIN" # métricas globales
curl http://localhost:8000/api/v1/admin/health -H "$ADMIN"         # qué integraciones tienes
```

## Parte 4 — Verificación del webhook (como lo hace Meta)

```bash
SLUG="clinica-sonrisa-9fb671"
# El verify token = sha256("<slug>:<META_VERIFY_TOKEN_SECRET>")[:32]
TOKEN=$(python -c "import hashlib;print(hashlib.sha256(f'$SLUG:dev-verify-token-secret'.encode()).hexdigest()[:32])")
curl "http://localhost:8000/webhooks/whatsapp/$SLUG?hub.mode=subscribe&hub.verify_token=$TOKEN&hub.challenge=PRUEBA123"
# → debe responder: PRUEBA123
```

## Parte 5 — Tests automatizados del backend

```bash
cd agentepro/backend
python -m pytest -q     # 18 pruebas (parsing, prompts, lead scoring, webhooks, provisioning)
```

---

## Checklist de validación (cuando ya tengas keys)

- [ ] GET del webhook de Meta devuelve el `hub.challenge`.
- [ ] Un WhatsApp real llega → Claude responde → aparece en el dashboard en vivo (Socket.io).
- [ ] Escalado → toast rojo en el dashboard + email.
- [ ] Llamada entrante → Retell contesta → transcript + resumen guardados.
- [ ] `POST /provision` crea Twilio + Retell + HubSpot reales (y hace rollback si algo falla).
- [ ] Lead caliente → deal en HubSpot.
- [ ] Post de Instagram generado con imagen real (fal.ai) → publicado.

> Más detalle de cada integración en [08 · Integraciones externas](08-integraciones-externas.md).

## Cómo agregar las keys
1. Edita `agentepro/backend/.env` (pon tus valores).
2. `docker compose restart backend worker`
3. Verifica con `curl .../admin/health` que la integración aparezca en `true`.

## Siguiente
➡️ [08 · Integraciones externas](08-integraciones-externas.md)
