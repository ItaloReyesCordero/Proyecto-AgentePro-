# Guía de despliegue paso a paso — AgentePro 2.0 🚀

> Para poner AgentePro en internet, en **un solo servidor (VPS)**, con dominio de **Porkbun**
> y **candado HTTPS automático**. Pensado para seguir al pie de la letra. Si algo falla,
> copia el error y me lo pasas. Fecha: 2026-06-03.

> **Lo bueno:** ya te dejé TODO preparado. Hay un solo comando para levantar todo el sistema
> (web + backend + base de datos + IA + candado HTTPS). Tú solo creas el servidor, apuntas el
> dominio y copias unos comandos.

---

## 🧭 Resumen de lo que vas a hacer
1. Crear un VPS (servidor en internet).
2. Apuntar tu dominio de Porkbun al VPS.
3. Instalar Docker en el VPS.
4. Subir el código y configurar 2 archivos.
5. Un comando para levantar todo.
6. Verificar que funciona con candado.

⏱️ Tiempo: ~45–60 min la primera vez.
💵 Costo: VPS ~$5–6/mes + dominio ~$10/año (Porkbun) + Anthropic (lo que consumas).

---

## PASO 1 — Crear el VPS (servidor)

### ¿Cuál te recomiendo?
**Hetzner Cloud** es el mejor precio/rendimiento y es fácil. Alternativa con más tutoriales en
español: **DigitalOcean** (un poco más caro). Cualquiera sirve.

| Proveedor | Plan recomendado | RAM | Precio aprox. | Nota |
|---|---|---|---|---|
| **Hetzner** (recomendado) | **CX22** (ubicación Ashburn, EE.UU.) | 4 GB | ~€4.5/mes | Mejor valor. Elige zona **US** (más cerca de Perú). |
| DigitalOcean | Droplet "Basic" 2GB/2CPU | 2 GB | ~$12/mes | Más tutoriales, datacenter NYC. |

> Mínimo 2 GB de RAM (este sistema corre base de datos + IA + web). 4 GB va más cómodo.

### Cómo crearlo (Hetzner)
1. Crea cuenta en https://www.hetzner.com/cloud → "Cloud Console".
2. **New Project** → **Add Server**.
3. **Location:** Ashburn, VA (US) — el más cercano a Perú.
4. **Image:** **Ubuntu 24.04**.
5. **Type:** CX22 (o el de 4 GB).
6. **SSH Key:** si sabes usar llaves SSH, súbela (más seguro). Si no, marca **password** y te
   mandan la contraseña de root por correo (más fácil para empezar).
7. Dale un nombre (ej. `agentepro`) y **Create**.
8. Anota la **IP pública** del servidor (ej. `5.161.xx.xx`). La usarás en el Paso 2.

---

## PASO 2 — Apuntar tu dominio de Porkbun al VPS

1. Entra a https://porkbun.com → **Domain Management** → tu dominio → **DNS**.
2. Borra registros A/AAAA viejos que apunten a otro lado (si los hay).
3. Crea estos registros (cambia `IP_DE_TU_VPS` por la IP del Paso 1):

| Tipo | Host (Name) | Answer / Value | TTL |
|---|---|---|---|
| **A** | (déjalo vacío o `@`) | `IP_DE_TU_VPS` | 600 |
| **A** | `www` | `IP_DE_TU_VPS` | 600 |

4. Guarda. **Espera 5–30 min** a que el dominio "apunte" al servidor (la propagación DNS).
   Para verificar desde tu PC: `ping tudominio.com` debe responder con la IP del VPS.

> Usaremos tu dominio "pelado" (ej. `agentepro.pe`). Si prefieres `app.tudominio.com`, crea el A
> en el host `app` y luego pon ese subdominio como DOMAIN en el Paso 5.

---

## PASO 3 — Entrar al servidor e instalar Docker

1. Desde tu PC (PowerShell o Git Bash), conéctate por SSH:
   ```
   ssh root@IP_DE_TU_VPS
   ```
   (acepta el "yes" y pon la contraseña que te llegó, o usa tu llave SSH).

2. Ya dentro del servidor, instala Docker con el script oficial:
   ```
   curl -fsSL https://get.docker.com | sh
   ```

3. Verifica:
   ```
   docker --version
   docker compose version
   ```
   Si ambos muestran una versión, Docker está listo. ✅

---

## PASO 4 — Subir el código al servidor

Tienes dos formas. La más fácil es **Git** (si subes el proyecto a GitHub privado). Si no, usa
la opción B (copiar desde tu PC).

### Opción A — con Git (recomendada)
```
cd /root
git clone TU_REPO_GIT agentepro
cd agentepro/agentepro
```
(la carpeta del proyecto donde están `docker-compose.deploy.yml`, `backend/`, `frontend/`).

### Opción B — copiar desde tu PC (sin Git)
Desde tu PC (PowerShell), en la carpeta del proyecto:
```
scp -r "D:\ESCRITORIO\PERSONAL\Proyecto AgentePro 2.0\agentepro" root@IP_DE_TU_VPS:/root/agentepro
```
Luego en el servidor: `cd /root/agentepro`.

> A partir de aquí, los comandos se ejecutan **dentro de la carpeta que tiene
> `docker-compose.deploy.yml`**.

---

## PASO 5 — Configurar los 2 archivos (.env)

### 5.1 — Archivo `.env` del despliegue (para Caddy y la base de datos)
Crea un archivo llamado `.env` en la carpeta del proyecto:
```
nano .env
```
Pega esto (cambia los valores):
```
DOMAIN=tudominio.com
ACME_EMAIL=italoreyescordero1@gmail.com
POSTGRES_PASSWORD=PonAquiUnaClaveLargaYsegura123
```
Guarda con `Ctrl+O`, Enter, y sal con `Ctrl+X`.

### 5.2 — Archivo `backend/.env` (la configuración de la app)
Copia la plantilla de producción y edítala:
```
cp backend/.env.production backend/.env
nano backend/.env
```
Asegúrate de poner/ajustar estas líneas (la **contraseña de Postgres debe ser la MISMA** del .env de arriba):
```
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://tudominio.com

# Base de datos (interna del propio servidor):
DATABASE_URL=postgresql+asyncpg://agentepro:PonAquiUnaClaveLargaYsegura123@postgres:5432/agentepro
DATABASE_URL_SYNC=postgresql://agentepro:PonAquiUnaClaveLargaYsegura123@postgres:5432/agentepro

# Redis (interno):
REDIS_URL=redis://redis:6379/0

# Para el respaldo automático de la base (mismos datos):
PGHOST=postgres
PGPORT=5432
PGUSER=agentepro
PGPASSWORD=PonAquiUnaClaveLargaYsegura123
PGDATABASE=agentepro

# Tu superadmin (ya viene una clave fuerte en .env.production; cámbiala si quieres):
SUPERADMIN_EMAIL=italoreyescordero1@gmail.com
SUPERADMIN_PASSWORD=(la que trae .env.production)

# La API de IA (la pones mañana cuando contrates Anthropic):
ANTHROPIC_API_KEY=

# Datos de cobro por Yape (ya configurados):
PAYMENT_YAPE_NUMBER=916085873
PAYMENT_ACCOUNT_HOLDER=Italo Eduardo Reyes Cordero
PAYMENT_CONTACT_WHATSAPP=51916085873
```
Guarda y sal (`Ctrl+O`, Enter, `Ctrl+X`).

> ⚠️ Las claves `SECRET_KEY`, `ADMIN_SECRET_KEY`, etc. ya vienen fuertes en `.env.production`.
> **No las cambies después de tener clientes** (rompe el cifrado de tokens de WhatsApp).

---

## PASO 6 — ¡Levantar todo! (un solo comando)

```
docker compose -f docker-compose.deploy.yml up -d --build
```
La primera vez tarda varios minutos (construye la web y el backend). Cuando termine:

```
docker compose -f docker-compose.deploy.yml ps
```
Debes ver todos los servicios "Up": caddy, frontend, backend, worker, beat, postgres, redis, backup.

Caddy saca el candado HTTPS **solo** en 1–2 minutos (necesita que el dominio del Paso 2 ya apunte
al VPS). Para ver que lo logró:
```
docker compose -f docker-compose.deploy.yml logs caddy | grep -i "certificate obtained\|serving"
```

---

## PASO 7 — Verificar que funciona ✅

1. Abre en tu navegador: **`https://tudominio.com`** → debe cargar la landing con el **candado 🔒**.
2. Entra a `https://tudominio.com/login` e inicia sesión con tu superadmin.
3. Revisa `https://tudominio.com/privacidad` y `/terminos` → deben cargar (las URLs que le darás a Meta).
4. Prueba salud del backend: `https://tudominio.com/health` → debe responder `{"status":"ok"}` o similar.

Si todo eso funciona, **ya estás en producción**. 🎉

---

## PASO 8 — (Después) Conectar WhatsApp real

Cuando tengas el acceso a WhatsApp Cloud API de un cliente, en Meta configurarás el webhook con:
- **URL de devolución:** `https://tudominio.com/webhooks/whatsapp/SLUG-DEL-NEGOCIO`
- **Verify token:** el que define el sistema para ese negocio.
- Las páginas de privacidad y términos: `https://tudominio.com/privacidad` y `/terminos`.

(Esto lo vemos juntos cuando llegues a ese punto.)

---

## 🔧 Comandos útiles del día a día

```
# Ver estado de los servicios
docker compose -f docker-compose.deploy.yml ps

# Ver logs (errores) de un servicio
docker compose -f docker-compose.deploy.yml logs backend --tail=50
docker compose -f docker-compose.deploy.yml logs caddy --tail=50

# Reiniciar todo
docker compose -f docker-compose.deploy.yml restart

# Apagar todo (sin borrar datos)
docker compose -f docker-compose.deploy.yml down

# Actualizar tras cambiar código (git pull y reconstruir)
git pull
docker compose -f docker-compose.deploy.yml up -d --build
```

---

## 🆘 Si algo falla (revisa esto antes de pasarme el error)

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El dominio no carga / "no se puede acceder" | El DNS aún no propaga | Espera 15–30 min; verifica `ping tudominio.com` = IP del VPS |
| Sale candado roto / "no seguro" | Caddy aún no sacó el certificado | Mira `logs caddy`; el dominio DEBE apuntar al VPS para que funcione |
| `backend` se reinicia en bucle | `backend/.env` mal (DB/clave) | `logs backend`; revisa que la contraseña de Postgres coincida en los 2 .env |
| "port 80 already in use" | Otra cosa usa el puerto 80 | `docker compose ... down` y revisa que no haya otro nginx/apache |
| El agente no responde | Falta `ANTHROPIC_API_KEY` | Ponla en `backend/.env` y `restart backend` |

**Para pasarme un error**, copia la salida de:
```
docker compose -f docker-compose.deploy.yml logs --tail=80
```

---

## ✅ Checklist final del despliegue
- [ ] VPS creado y con su IP anotada.
- [ ] Dominio de Porkbun apuntando a la IP (registros A).
- [ ] Docker instalado en el VPS.
- [ ] Código subido al VPS.
- [ ] `.env` del despliegue creado (DOMAIN, ACME_EMAIL, POSTGRES_PASSWORD).
- [ ] `backend/.env` configurado (DB interna, FRONTEND_URL, claves).
- [ ] `docker compose -f docker-compose.deploy.yml up -d --build` corriendo.
- [ ] `https://tudominio.com` carga con candado 🔒.
- [ ] Login del superadmin funciona.
- [ ] (Mañana) `ANTHROPIC_API_KEY` puesta → el agente responde.
