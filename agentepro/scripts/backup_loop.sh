#!/bin/sh
# ---------------------------------------------------------------------------
# Bucle del servicio de backups (contenedor "backup" del docker-compose).
#
# Hace un backup al arrancar (útil para verificar que todo funciona) y luego
# repite cada BACKUP_INTERVAL_SECONDS segundos. Si un backup falla, NO mata el
# servicio: registra el error y reintenta en el siguiente ciclo.
#
#   BACKUP_INTERVAL_SECONDS  segundos entre backups (def: 86400 = 1 día)
# ---------------------------------------------------------------------------
set -eu

INTERVAL="${BACKUP_INTERVAL_SECONDS:-86400}"

log() {
    printf '%s [backup] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"
}

log "Servicio de backups iniciado. Intervalo: ${INTERVAL}s. Carpeta: ${BACKUP_DIR:-/backups}"

# Si hay copia off-site configurada, asegura curl (la imagen alpine no lo trae).
if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_KEY:-}" ]; then
    if command -v curl >/dev/null 2>&1; then
        log "Copia off-site a Supabase ACTIVADA (bucket: ${SUPABASE_BACKUP_BUCKET:-db-backups})."
    else
        log "Instalando curl para la copia off-site a Supabase..."
        if apk add --no-cache curl >/dev/null 2>&1; then
            log "curl instalado. Copia off-site a Supabase ACTIVADA."
        else
            log "AVISO: no se pudo instalar curl; la copia off-site se omitirá."
        fi
    fi
else
    log "Copia off-site a Supabase desactivada (define SUPABASE_URL y SUPABASE_SERVICE_KEY para activarla)."
fi

while true; do
    if ! sh /scripts/backup_db.sh; then
        log "El backup falló; se reintentará en el próximo ciclo."
    fi
    log "Durmiendo ${INTERVAL}s hasta el próximo backup."
    sleep "$INTERVAL"
done
