#!/bin/sh
# ---------------------------------------------------------------------------
# Restaura un backup de Postgres creado por backup_db.sh.
#
# ⚠️  REEMPLAZA los datos actuales de la base por los del backup.
#
# Lee la conexión desde PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE.
#
# Uso: sh restore_db.sh /backups/agentepro_20260601_030000.dump
# ---------------------------------------------------------------------------
set -eu

DB_NAME="${PGDATABASE:-agentepro}"

log() {
    printf '%s [restore] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"
}

backup_file="${1:-}"
if [ -z "$backup_file" ]; then
    log "ERROR: indica la ruta del backup. Ej: sh restore_db.sh /backups/archivo.dump"
    exit 2
fi
if [ ! -f "$backup_file" ]; then
    log "ERROR: no existe el archivo '${backup_file}'."
    exit 2
fi

log "Restaurando '${backup_file}' sobre la base '${DB_NAME}'..."
# --clean --if-exists: elimina los objetos previos antes de recrearlos.
# --no-owner --no-privileges: evita errores de roles/permisos al restaurar.
pg_restore --no-owner --no-privileges --clean --if-exists --dbname="$DB_NAME" "$backup_file"
log "Restauración completada."
