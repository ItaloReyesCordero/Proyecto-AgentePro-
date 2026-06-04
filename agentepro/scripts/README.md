# Scripts de operación — Backups de Postgres

Backups automáticos de la base de datos de AgentePro 2.0.

## Qué hace

El servicio `backup` del `docker-compose.yml` levanta un contenedor pequeño
(imagen `postgres:16-alpine`, la misma versión que la BD) que:

1. Hace **un backup al arrancar** (para verificar que funciona).
2. Repite **cada `BACKUP_INTERVAL_SECONDS`** (por defecto `86400` = 1 día).
3. Guarda cada copia en `agentepro/backups/` (en el host).
4. **Rota**: borra las copias con más de `BACKUP_RETENTION_DAYS` días (def. 7 en dev, 14 en prod).

Cada copia es un archivo `agentepro_AAAAMMDD_HHMMSS.dump` en formato *custom* de
Postgres (comprimido y restaurable con `pg_restore`).

## Archivos

| Script | Para qué |
|---|---|
| `backup_db.sh` | Hace **un** volcado, lo sube a Supabase (si está configurado) y rota los antiguos. |
| `backup_loop.sh` | Bucle del servicio: backup al arrancar + cada intervalo. No se cae si un backup falla. |
| `restore_db.sh` | **Restaura** un backup (⚠️ reemplaza los datos actuales). |
| `upload_supabase.sh` | Sube **un** `.dump` a Supabase Storage (copia off-site). Lo llama `backup_db.sh`. |
| `download_supabase.sh` | Lista/descarga copias desde Supabase (recuperación ante desastre). |

Leen la conexión de las variables estándar de Postgres: `PGHOST`, `PGPORT`,
`PGUSER`, `PGPASSWORD`, `PGDATABASE`.

## Uso

```bash
# Levantar el servicio de backups (ya incluido en docker compose up -d)
cd agentepro
docker compose up -d backup

# Ver el log del servicio (confirma "Backup OK: ...")
docker compose logs -f backup

# Forzar un backup manual ahora mismo
docker compose exec backup sh /scripts/backup_db.sh

# Listar los backups
ls -lh backups/
```

### Restaurar un backup

```bash
# El archivo debe estar en agentepro/backups/ (visible como /backups dentro)
docker compose exec backup sh /scripts/restore_db.sh /backups/agentepro_20260601_030000.dump
```

> ⚠️ La restauración usa `--clean --if-exists`: borra los objetos actuales y los
> recrea desde el backup. Úsala solo para recuperar tras una pérdida de datos.

## Copia OFF-SITE a Supabase Storage (ante desastre del servidor)

Además de guardar el `.dump` en disco, cada backup se **sube a Supabase Storage**
si defines las credenciales. Así, si pierdes el servidor entero, las copias
siguen a salvo en la nube de Supabase.

### Activarla (una sola vez)

1. En el panel de Supabase: **Storage → New bucket**, nombre `db-backups`,
   marcado como **Private** (privado). Es un bucket distinto al de media.
2. **Settings → API**: copia la **`service_role` key** (la secreta, NO la `anon`).
3. Ponlas donde el servicio `backup` las lee:
   - **Dev** (`docker-compose.yml`): crea `agentepro/.env` con:
     ```
     SUPABASE_URL=https://TUPROYECTO.supabase.co
     SUPABASE_SERVICE_KEY=eyJ...service_role...
     ```
   - **Prod** (`docker-compose.prod.yml`): añade esas dos líneas a `backend/.env`.
4. Reinicia el servicio: `docker compose up -d backup`.

En el log verás `Copia off-site a Supabase ACTIVADA` y, tras cada backup,
`Copia off-site OK (HTTP 200): db-backups/agentepro/...`.

Variables (todas opcionales salvo las dos primeras):

| Variable | Def | Para qué |
|---|---|---|
| `SUPABASE_URL` | — | URL del proyecto Supabase. |
| `SUPABASE_SERVICE_KEY` | — | Clave `service_role` (permite escribir en buckets privados). |
| `SUPABASE_BACKUP_BUCKET` | `db-backups` | Bucket destino. |
| `SUPABASE_BACKUP_PREFIX` | `agentepro` | Carpeta dentro del bucket. |
| `SUPABASE_BACKUP_KEEP` | `30` | Copias remotas a conservar (`0` = no borrar nunca). |

> Si dejas las variables vacías, la subida **se omite sola** y solo quedan los
> backups locales (no rompe nada).

### Recuperar desde Supabase (si perdiste el servidor)

```bash
# Levanta solo el servicio backup en el servidor nuevo (con las SUPABASE_* puestas)
docker compose up -d backup

# 1) Ver qué copias hay en la nube
docker compose exec backup sh /scripts/download_supabase.sh list

# 2) Descargar la que quieras a /backups
docker compose exec backup sh /scripts/download_supabase.sh agentepro_20260601_030000.dump

# 3) Restaurarla sobre la base
docker compose exec backup sh /scripts/restore_db.sh /backups/agentepro_20260601_030000.dump
```

## Producción

En `docker-compose.prod.yml` el servicio `backup` lee `PGHOST/PGPORT/PGUSER/
PGPASSWORD/PGDATABASE` desde `backend/.env` (ponlos con los mismos datos de tu
`DATABASE_URL`). Si tu proveedor de BD (Supabase, Railway) ya hace backups
gestionados, este servicio es una **copia extra opcional**.

## Notas

- Los `.dump` están en `.gitignore` (no se suben al repo).
- Los scripts usan saltos de línea **LF** (necesario para correr en Alpine).
- Para descargar un backup fuera del servidor, cópialo con `docker compose cp`
  o súbelo a almacenamiento externo (S3/Supabase) — recomendado para
  desastres del servidor entero.
