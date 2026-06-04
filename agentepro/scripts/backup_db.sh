#!/bin/sh
# ---------------------------------------------------------------------------
# Backup de la base de datos Postgres de AgentePro 2.0.
#
# Hace un volcado en formato "custom" (comprimido y restaurable con pg_restore)
# y luego borra los backups más antiguos que BACKUP_RETENTION_DAYS días.
#
# Lee la conexión desde las variables estándar de Postgres:
#   PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
#
# Variables propias:
#   BACKUP_DIR             carpeta destino (def: /backups)
#   BACKUP_RETENTION_DAYS  días a conservar (def: 7)
#
# Uso: sh backup_db.sh
# ---------------------------------------------------------------------------
set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
DB_NAME="${PGDATABASE:-agentepro}"

log() {
    printf '%s [backup] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"
}

mkdir -p "$BACKUP_DIR"

timestamp="$(date '+%Y%m%d_%H%M%S')"
outfile="${BACKUP_DIR}/${DB_NAME}_${timestamp}.dump"

log "Iniciando volcado de la base '${DB_NAME}' en ${PGHOST:-localhost}..."

# --format=custom: archivo comprimido y restaurable selectivamente con pg_restore.
# --no-owner / --no-privileges: el volcado se puede restaurar en otro rol sin errores.
if pg_dump --no-owner --no-privileges --format=custom --file="$outfile"; then
    size="$(wc -c < "$outfile" | tr -d ' ')"
    log "Backup OK: ${outfile} (${size} bytes)"
else
    status=$?
    log "ERROR: pg_dump falló (código ${status}). Se elimina el archivo parcial."
    rm -f "$outfile"
    exit "$status"
fi

# Copia OFF-SITE a Supabase Storage (si está configurada). Se hace ANTES de la
# rotación local para que un backup nuevo quede a salvo cuanto antes. Si la
# subida falla, NO se aborta: el backup local ya está guardado.
if [ -f /scripts/upload_supabase.sh ]; then
    if ! sh /scripts/upload_supabase.sh "$outfile"; then
        log "AVISO: la copia off-site a Supabase falló (el backup local SÍ se guardó)."
    fi
fi

# Rotación: cuenta y elimina los backups con más de RETENTION_DAYS días.
old_count="$(find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" -type f -mtime "+${RETENTION_DAYS}" | wc -l | tr -d ' ')"
if [ "$old_count" -gt 0 ]; then
    find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" -type f -mtime "+${RETENTION_DAYS}" -exec rm -f {} +
fi
log "Rotación: ${old_count} backup(s) con más de ${RETENTION_DAYS} días eliminados."
log "Listo."
