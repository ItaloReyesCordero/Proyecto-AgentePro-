# NEXT_STEPS — Guía post-build

Esta guía te lleva desde el código construido hasta tu primer cliente cobrando.

## 1. Consola por consola — dónde obtener cada API key

| Servicio | URL | Qué copiar |
|---|---|---|
| Anthropic | https://console.anthropic.com | `ANTHROPIC_API_KEY` |
| Meta (WhatsApp + Instagram) | https://developers.facebook.com | `META_APP_ID`, `META_APP_SECRET`, IDs de Instagram |
| Twilio | https://console.twilio.com | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` |
| Retell AI | https://dashboard.retellai.com | `RETELL_API_KEY`, `RETELL_WEBHOOK_SECRET` |
| HubSpot | https://app.hubspot.com (App privada) | `HUBSPOT_ACCESS_TOKEN` |
| Modal | https://modal.com | `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` |
| fal.ai | https://fal.ai/dashboard/keys | `FAL_KEY` |
| Supabase | https://supabase.com | `SUPABASE_URL`, `SUPABASE_KEY`, `DATABASE_URL` |
| Culqi | https://culqi.com | `CULQI_PUBLIC_KEY`, `CULQI_SECRET_KEY` |
| Resend | https://resend.com | `RESEND_API_KEY` |
| OpenAI (Whisper) | https://platform.openai.com | `OPENAI_API_KEY` |

## 2. Orden de setup recomendado

1. **Supabase** → base de datos + storage (necesaria para arrancar).
2. **Anthropic** → sin esto el agente no responde.
3. **Meta WhatsApp** → el canal principal.
4. **Resend** → emails de bienvenida.
5. **HubSpot** → CRM (opcional al inicio).
6. **Twilio + Retell** → voz (cuando vendas el plan que lo incluye).
7. **fal.ai** → Instagram (Pro/Enterprise).
8. **Culqi** → cobros automáticos.
9. **Modal** → automatizaciones programadas.

> Todos los servicios externos degradan con gracia: si una key falta, esa función se desactiva sin romper la app (revisa `/api/v1/admin/health`).

## 3. Testing local con ngrok

```bash
ngrok http 8000
# Usa la URL pública para los webhooks de Meta/Retell/Twilio/Culqi:
#   https://xxxx.ngrok.io/webhooks/whatsapp/<tenant_slug>
```

1. Registra un tenant (`/api/v1/auth/register`).
2. En *Configuración* copia el `webhook_verify_token`.
3. Configura el webhook en Meta y verifica (GET debe devolver el challenge).
4. Envía un WhatsApp a tu número de prueba y observa la respuesta en el dashboard.

## 4. Primer deploy

**Railway (backend):** conecta el repo, apunta a `backend/`, agrega Postgres + Redis, define las variables de entorno. El start command corre migraciones automáticamente.

**Vercel (frontend):** importa `frontend/`, define `VITE_API_URL` si separas dominios; el SPA rewrite ya está configurado.

## 5. Primer cliente

1. `POST /api/v1/provision` con `X-Admin-Key` (sin cobro) o con `culqi_token` (con cobro):
   ```json
   {
     "business_name": "Clínica Dental Sonrisa",
     "business_type": "healthcare",
     "owner_name": "Ana Pérez",
     "owner_email": "ana@sonrisa.pe",
     "owner_phone": "+51999111222",
     "plan": "professional",
     "culqi_token": "tkn_..."
   }
   ```
2. El sistema crea tenant + agente + voz + Twilio + Retell + HubSpot + automatizaciones y envía el email de bienvenida.
3. El cliente conecta su WhatsApp con la URL/token del email.

## 6. Checklist antes de cobrar al primer cliente

- [ ] El webhook GET de Meta devuelve el `hub.challenge`.
- [ ] Un WhatsApp entrante recibe respuesta de Claude y aparece en el dashboard en vivo.
- [ ] El escalado a humano notifica (toast + email).
- [ ] Una llamada entrante se enruta a Retell y genera transcripción + resumen.
- [ ] El provisioning hace rollback si falla un paso externo.
- [ ] Un lead caliente crea un deal en HubSpot.
- [ ] Se genera y aprueba un post de Instagram.
- [ ] `uv run pytest` pasa y `npm run build` compila sin errores.
