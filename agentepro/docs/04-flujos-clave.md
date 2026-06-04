# 04 · Flujos clave

Diagramas de secuencia de los procesos más importantes. Cada uno indica el archivo donde vive la lógica.

---

## A. Mensaje entrante de WhatsApp (el flujo estrella)

```mermaid
sequenceDiagram
    participant C as Cliente final
    participant M as Meta (WhatsApp)
    participant W as webhooks/meta_whatsapp.py
    participant H as services/whatsapp/webhook_handler.py
    participant AI as services/ai/agent.py (Claude)
    participant DB as PostgreSQL
    participant S as Socket.io → Dashboard

    C->>M: "Hola, quiero una cita"
    M->>W: POST /webhooks/whatsapp/{slug}
    W->>W: Verifica firma HMAC-SHA256
    W-->>M: 200 OK (inmediato)
    Note over W,H: Procesa en segundo plano
    W->>H: handle_inbound_message()
    H->>DB: ¿wa_message_id ya existe? (anti-duplicado)
    H->>DB: get/create Contact + Conversation
    H->>DB: guarda mensaje entrante
    H->>S: emite "new_message" + "agent_typing"
    alt Bot activo (no hay humano)
        H->>AI: process_whatsapp_message()
        AI->>AI: construye system prompt dinámico
        AI->>Claude: messages.create(...)
        Claude-->>AI: respuesta + bloque <!--META:...-->
        AI->>AI: parsea intent, lead_score, acciones
        AI-->>H: AgentResponse
        H->>M: envía respuesta al cliente
        H->>DB: guarda mensaje saliente + actualiza lead
        H->>S: emite "agent_response" / "lead_score_updated"
        opt Escalado detectado
            H->>S: emite "escalation_needed" (+ email)
        end
        opt Lead caliente y HubSpot activo
            H->>HubSpot: crea/actualiza contacto y deal
        end
    else Humano tomó el control
        H-->>H: no responde (espera al humano)
    end
```

**Sin `ANTHROPIC_API_KEY`:** todo el flujo corre igual, pero `Claude` falla y el agente devuelve un mensaje de respaldo ("Disculpe, tuve un problema técnico…"), que igual se guarda. Por eso **puedes probar el flujo completo sin keys**.

---

## B. Llamada de voz entrante

```mermaid
sequenceDiagram
    participant C as Cliente final
    participant T as Twilio
    participant TV as webhooks/twilio_voice.py
    participant R as Retell AI
    participant RW as webhooks/retell.py
    participant CH as services/voice/call_handler.py
    participant SUM as services/ai/call_summarizer.py (Claude)
    participant DB as PostgreSQL

    C->>T: llama al número del negocio
    T->>TV: POST /webhooks/twilio/voice/{slug}
    TV->>DB: crea Call (inbound, initiated)
    TV-->>T: TwiML <Connect><Stream wss://retell…>
    T->>R: stream de audio
    R-->>C: conversación de voz (Claude responde)
    R->>RW: evento call_started / call_ended / call_analyzed
    RW->>CH: process_retell_event()
    CH->>DB: actualiza Call (duración, transcript, grabación)
    CH->>SUM: summarize(transcript)
    SUM->>Claude: analiza la llamada
    Claude-->>SUM: resumen JSON (puntos, sentimiento, próxima acción)
    CH->>DB: guarda CallSummary + actualiza lead
    CH->>HubSpot: nota de actividad (si está conectado)
```

---

## C. Auto-provisioning (alta de un nuevo negocio)

```mermaid
sequenceDiagram
    participant Admin as Tú (X-Admin-Key) o Pago Culqi
    participant P as api/v1/provisioning.py
    participant TP as services/provisioning/tenant_provisioner.py
    participant DB as PostgreSQL
    participant EXT as Twilio / Retell / HubSpot
    participant MAIL as Resend

    Admin->>P: POST /api/v1/provision {datos del negocio}
    opt Hay culqi_token
        P->>Culqi: cobra el plan
    end
    P->>TP: provision_new_tenant()
    TP->>DB: crea Tenant + Usuario dueño
    TP->>DB: crea AgentConfig (FAQs por rubro) + VoiceConfig
    TP->>EXT: compra número Twilio
    TP->>EXT: crea LLM + agente de voz (Retell)
    TP->>EXT: crea empresa en HubSpot
    TP->>DB: crea automatizaciones según plan
    TP->>DB: marca is_provisioned = true
    TP->>MAIL: email de bienvenida (accesos + webhook URL)
    TP-->>P: {tenant_id, dashboard_url, webhook_url, phone_number, access_token}
    Note over TP,EXT: Si CUALQUIER paso externo falla →<br/>libera número Twilio, borra agente Retell,<br/>rollback de DB y error 500
```

**Sin keys externas:** el provisioning **igual funciona**: crea el tenant, usuario, configs y automatizaciones en la base; los pasos de Twilio/Retell/HubSpot simplemente devuelven `None` (degradación con gracia) y `phone_number` queda en `null`.

---

## D. Generación y publicación de Instagram

```mermaid
sequenceDiagram
    participant CRON as Modal (lunes 8am)
    participant G as services/instagram/post_generator.py
    participant CL as Claude
    participant FAL as fal.ai
    participant DB as PostgreSQL
    participant Owner as Dueño (Dashboard)
    participant PUB as Modal (cada hora) → scheduler.py
    participant IG as Instagram Graph API

    CRON->>G: generate_and_store_post(tema)
    G->>CL: genera caption + hashtags + prompt de imagen
    G->>FAL: genera imagen (flux/schnell)
    G->>DB: guarda post (status=draft, pending_approval)
    G-->>Owner: notifica "posts listos para revisar"
    Owner->>DB: aprueba (status=scheduled, scheduled_for)
    PUB->>DB: busca posts vencidos (scheduled_for <= ahora)
    PUB->>IG: publica (media + media_publish)
    PUB->>DB: status=published, guarda media_id
```

---

## E. Automatizaciones programadas

```mermaid
flowchart LR
    subgraph Modal["Modal (cron en la nube)"]
        F1["follow_up_leads<br/>(diario 9am Perú)"]
        F2["weekly_instagram_posts<br/>(lunes)"]
        F3["publish_scheduled_posts<br/>(cada hora)"]
        F4["send_weekly_reports<br/>(lunes)"]
    end
    subgraph Celery["Celery + Redis"]
        C1["emails transaccionales"]
        C2["recordatorios de citas"]
    end
    Modal --> DB[("DB")]
    Celery --> DB
```

## Siguiente
➡️ [05 · Referencia de la API](05-api-referencia.md)
