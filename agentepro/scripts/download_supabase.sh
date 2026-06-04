#!/bin/sh
# ---------------------------------------------------------------------------
# Recuperación ante desastre: lista o descarga backups desde Supabase Storage.
#
# Útil cuando el servidor entero se perdió y ya no tienes los .dump locales.
#
# Variables (las mismas que upload_supabase.sh):
#   SUPABASE_URL, SUPABASE_SERVICE_KEY,
#   SUPABASE_BACKUP_BUCKET (def: db-backups), SUPABASE_BACKUP_PREFIX (def: agentepro)
#
# Uso:
#   sh download_supabase.sh list                      # lista las copias remotas
#   sh download_supabase.sh <archivo.dump> [destino]  # descarga (def: /backups)
# ---------------------------------------------------------------------------
set -eu

log() { printf '%s [download] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"; }

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_KEY:-}" ]; then
    log "ERROR: define SUPABASE_URL y SUPABASE_SERVICE_KEY."
    exit 2
fi
command -v curl >/dev/null 2>&1 || { log "ERROR: curl no está instalado."; exit 3; }

URL="${SUPABASE_URL%/}"
BUCKET="${SUPABASE_BACKUP_BUCKET:-db-backups}"
PREFIX="${SUPABASE_BACKUP_PREFIX:-agentepro}"
arg="${1:-}"

if [ -z "$arg" ] || [ "$arg" = "list" ]; then
    resp="$(curl -sS -X POST "${URL}/storage/v1/object/list/${BUCKET}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"prefix\":\"${PREFIX}/\",\"limit\":1000,\"sortBy\":{\"column\":\"name\",\"order\":\"desc\"}}")"
    names="$(printf '%s' "$resp" | grep -o '"name":"[^"]*"' | sed 's/"name":"//; s/"$//')"
    if [ -z "$names" ]; then
        log "No hay copias en ${BUCKET}/${PREFIX}/ (o la respuesta fue: $(printf '%s' "$resp" | head -c 200))"
        exit 0
    fi
    log "Copias en Supabase (${BUCKET}/${PREFIX}/), de más reciente a más antigua:"
    printf '%s\n' "$names"
    exit 0
fi

dest_dir="${2:-/backups}"
mkdir -p "$dest_dir"
out="${dest_dir}/${arg}"
endpoint="${URL}/storage/v1/object/${BUCKET}/${PREFIX}/${arg}"

log "Descargando ${arg} -> ${out} ..."
code="$(curl -sS -o "$out" -w '%{http_code}' \
    -X GET "$endpoint" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}")" || { log "ERROR: curl falló."; exit 4; }

if [ "$code" != "200" ]; then
    log "ERROR: Supabase respondió HTTP ${code}. Respuesta:"
    head -c 500 "$out" 2>/dev/null || true
    printf '\n'
    rm -f "$out"
    exit 5
fi
log "Descarga OK: ${out} ($(wc -c < "$out" | tr -d ' ') bytes)"
log "Restaura con: sh /scripts/restore_db.sh ${out}"
