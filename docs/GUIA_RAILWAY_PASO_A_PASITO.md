# 🚂 Guía Railway — paso a pasito (clic por clic)

Guía súper detallada para desplegar **AgentePro** en Railway desde el repo
`https://github.com/ItaloReyesCordero/Proyecto-AgentePro-`.

> Lo marcado con `<<...>>` lo copias de tu archivo **`agentepro/backend/.env`**
> (ábrelo con el Bloc de notas). No subas ese archivo a ningún lado: es tu llave.

---

## FASE 1 — Crear cuenta y proyecto

1. Abre el navegador y entra a **railway.app**
2. Botón **"Login"** (arriba a la derecha) → **"Login with GitHub"** → autoriza con tu cuenta **ItaloReyesCordero**.
3. En el panel, botón morado **"New Project"**.
4. Clic en **"Deploy from GitHub repo"**.
5. La primera vez pide permiso: **"Configure GitHub App"** → marca el repo **`Proyecto-AgentePro-`** (o "All repositories") → **"Install & Authorize"**.
6. Vuelve a Railway, aparece tu repo → clic en **`Proyecto-AgentePro-`** → **"Deploy Now"**.
7. Railway crea un "servicio" y empieza a construir. **El primer build va a fallar — es normal** (aún no le dijimos la carpeta). Sigue a la Fase 2.

## FASE 2 — Decirle dónde está el código

8. Clic en la **caja del servicio** (el rectángulo con el nombre del repo).
9. Pestaña **"Settings"**.
10. Sección **"Source"** → campo **"Root Directory"** → escribe exactamente:
    ```
    agentepro
    ```
11. Sección **"Build"**:
    - **"Builder"** → elige **"Dockerfile"**.
    - **"Dockerfile Path"** → escribe exactamente:
      ```
      Dockerfile.railway
      ```
12. Railway guarda solo.

## FASE 3 — Base de datos PostgreSQL y Redis

13. Arriba a la derecha del lienzo, botón **"+ New"** (o **"Create"**).
14. **"Database"** → **"Add PostgreSQL"**. Aparece la caja "Postgres".
15. Otra vez **"+ New"** → **"Database"** → **"Add Redis"**. Aparece la caja "Redis".

## FASE 4 — Variables de entorno (el corazón)

16. Clic en la **caja de tu servicio** (el del repo, NO Postgres) → pestaña **"Variables"**.
17. Botón **"Raw Editor"** — deja pegar todo de golpe.
18. **Pega este bloque** y reemplaza los `<<...>>` con los valores de tu `agentepro/backend/.env`:

```
ENVIRONMENT=production
DEBUG=false
ALLOW_FREE_SIGNUP=false
FRONTEND_URL=https://tuagentepro.xyz
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SUPERADMIN_EMAIL=italoreyescordero1@gmail.com
SUPERADMIN_NAME=Italo Reyes
SUPERADMIN_PASSWORD=PonUnaClaveFuerteQueRecuerdes123
SECRET_KEY=<<valor de SECRET_KEY= de tu .env>>
ADMIN_SECRET_KEY=<<valor de ADMIN_SECRET_KEY= de tu .env>>
ANTHROPIC_API_KEY=<<valor de ANTHROPIC_API_KEY= de tu .env>>
TWILIO_ACCOUNT_SID=<<valor de TWILIO_ACCOUNT_SID= de tu .env>>
TWILIO_AUTH_TOKEN=<<valor de TWILIO_AUTH_TOKEN= de tu .env>>
TWILIO_WHATSAPP_FROM=+14155238886
RETELL_API_KEY=<<valor de RETELL_API_KEY= de tu .env>>
PAYMENT_YAPE_NUMBER=916085873
PAYMENT_ACCOUNT_HOLDER=Italo Eduardo Reyes Cordero
PAYMENT_CONTACT_WHATSAPP=51916085873
```

19. Ojo con 3 líneas:
    - **`SUPERADMIN_PASSWORD`**: pon una clave que **recordarás** — con esa entras como dueño de la plataforma (superadmin) la primera vez.
    - **`DATABASE_URL` y `REDIS_URL`**: déjalas tal cual (`${{Postgres.DATABASE_URL}}` y `${{Redis.REDIS_URL}}`). Railway las conecta solo.
    - **`FRONTEND_URL`**: ponla con tu dominio final, o con la URL de prueba de Railway mientras tanto (ver Fase 5).
20. Clic en **"Update Variables"** / **"Save"**. Railway **redepliega solo** y **aplica las migraciones automáticamente** (incluidas las de los 4 planes).

**Opcionales (agrégalas después con "+ New Variable"):** `RESEND_API_KEY`, `RESEND_FROM_EMAIL=onboarding@resend.dev`, `FAL_KEY`, `META_APP_SECRET`. Sin ellas funciona igual (degradan solas).

> No hace falta poner las variables `PLAN_*`: los precios/topes nuevos
> (149/249/449/799 y 200/400/1500/4000) ya son los valores por defecto en el código.

## FASE 5 — Verificar que prendió + dominio de prueba

21. Pestaña **"Deployments"** → el último debe ponerse **"Success"** (verde). Si sale rojo, abre el log y revísalo (o pásalo para diagnóstico).
22. Pestaña **"Settings"** → **"Networking"** → botón **"Generate Domain"**. Te da una URL `algo.up.railway.app`.
23. Ábrela: debe verse la landing de **AgentePro** con los 4 planes. 🎉
24. Mientras uses esa URL de prueba, cambia `FRONTEND_URL` a `https://algo.up.railway.app`. Cuando pongas tu dominio real, la cambias a `https://tuagentepro.xyz`.

## FASE 6 — Tu dominio tuagentepro.xyz

25. **Settings → Networking → "Custom Domain"** → escribe `tuagentepro.xyz` → **"Add Domain"**.
26. Railway muestra un **CNAME** (ej. `xxxx.up.railway.app`). Cópialo.
27. En **Porkbun** → DNS de `tuagentepro.xyz` → agrega un registro **CNAME** apuntando a ese valor. (Para el dominio raíz, Porkbun puede usar "ALIAS/ANAME"; si solo permite CNAME en `www`, usa `www.tuagentepro.xyz` y redirige la raíz.)
28. Cuando Railway marque el dominio en verde, deja `FRONTEND_URL=https://tuagentepro.xyz`.

## FASE 7 — (Opcional) Worker para citas y recordatorios

29. **"+ New"** → **"Empty Service"** → conéctalo al mismo repo (`Proyecto-AgentePro-`).
30. En sus **Settings**: Root Directory `agentepro`, Dockerfile Path `Dockerfile.railway`.
31. **Start Command:**
    ```
    celery -A app.workers.celery_app worker --beat --loglevel=info
    ```
32. Cópiale las **mismas variables** del servicio web. (Sin este worker el sistema funciona; solo no se envían recordatorios automáticos de citas.)

## FASE 8 — Conectar WhatsApp y voz al dominio

33. En **Twilio** → tu número de WhatsApp → **"When a message comes in"**:
    ```
    https://tuagentepro.xyz/webhooks/twilio/whatsapp/SLUG-DEL-NEGOCIO
    ```
34. En **Retell** → el agente del negocio → **Webhook URL**:
    ```
    https://tuagentepro.xyz/webhooks/retell/SLUG-DEL-NEGOCIO
    ```
    (El SLUG es el identificador del negocio, p. ej. `barberia-don-pepe-af0a24`.)

---

### Recordatorios honestos
- El `.env` NO está en GitHub (a propósito): por eso las variables se ponen a mano en Railway.
- Para WhatsApp real (sin "join"), cada negocio necesita su número registrado como **WhatsApp Sender en Twilio** (Twilio lo aprueba con Meta). El sandbox del +14155238886 es solo para pruebas.
- Si un deploy sale rojo: abre **Deployments → el deploy → View Logs** y revisa el error (lo más común: falta una variable o un typo en `DATABASE_URL`).
