#!/bin/sh
# ---------------------------------------------------------------------------
# Sube un backup .dump a Supabase Storage (copia OFF-SITE para desastres).
#
# Degrada con elegancia: si no están SUPABASE_URL / SUPABASE_SERVICE_KEY,
# NO hace nada y devuelve 0 (el backup local ya quedó guardado).
#
# Variables:
#   SUPABASE_URL              https://<proyecto>.supabase.co  (sin / final)
#   SUPABASE_SERVICE_KEY      service_role key (NO la anon/public key)
#   SUPABASE_BACKUP_BUCKET    bucket destino           (def: db-backups)
#   SUPABASE_BACKUP_PREFIX    carpeta dentro del bucket (def: agentepro)
#   SUPABASE_BACKUP_KEEP      nº de copias remotas a conservar (def: 30, 0=todas)
#
# Uso: sh upload_supabase.sh /backups/agentepro_AAAAMMDD_HHMMSS.dump
# ---------------------------------------------------------------------------
set -eu

log() { printf '%s [upload] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"; }

file="${1:-}"

# --- Subida desactivada (sin credenciales): salir en silencio, sin fallar ----
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_KEY:-}" ]; then
    log "SUPABASE_URL/SUPABASE_SERVICE_KEY no definidas; se omite la copia off-site."
    exit 0
fi

if [ -z "$file" ] || [ ! -f "$file" ]; then
    log "ERROR: el archivo a subir no existe: '${file}'."
    exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
    log "ERROR: curl no está instalado; no se puede subir a Supabase."
    exit 3
fi

URL="${SUPABASE_URL%/}"
BUCKET="${SUPABASE_BACKUP_BUCKET:-db-backups}"
PREFIX="${SUPABASE_BACKUP_PREFIX:-agentepro}"
KEEP="${SUPABASE_BACKUP_KEEP:-30}"

base="$(basename "$file")"
object="${PREFIX}/${base}"
endpoint="${URL}/storage/v1/object/${BUCKET}/${object}"

log "Subiendo ${base} a Supabase (${BUCKET}/${object})..."
code="$(curl -sS -o /tmp/sb_up.out -w '%{http_code}' \
    -X POST "$endpoint" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
    -H "x-upsert: true" \
    -H "Content-Type: application/octet-stream" \
    --data-binary "@${file}")" || { log "ERROR: curl falló (problema de red)."; exit 4; }

if [ "$code" != "200" ] && [ "$code" != "201" ]; then
    log "ERROR: Supabase respondió HTTP ${code}:"
    head -c 500 /tmp/sb_up.out 2>/dev/null || true
    printf '\n'
    exit 5
fi
log "Copia off-site OK (HTTP ${code}): ${BUCKET}/${object}"

# --- Rotación remota (best-effort, nunca hace fallar el script) -------------
# Conserva las KEEP copias más recientes. Los nombres llevan timestamp, así que
# ordenan cronológicamente; se borran las más antiguas que sobren.
prune_remote() {
    [ "${KEEP}" = "0" ] && return 0
    list="${URL}/storage/v1/object/list/${BUCKET}"
    resp="$(curl -sS -X POST "$list" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"prefix\":\"${PREFIX}/\",\"limit\":1000,\"sortBy\":{\"column\":\"name\",\"order\":\"asc\"}}" \
        2>/dev/null)" || return 0
    names="$(printf '%s' "$resp" | grep -o '"name":"[^"]*"' | sed 's/"name":"//; s/"$//')"
    [ -z "$names" ] && return 0
    total="$(printf '%s\n' "$names" | grep -c '.' || true)"
    [ "$total" -le "$KEEP" ] && return 0
    drop=$((total - KEEP))
    printf '%s\n' "$names" | head -n "$drop" | while IFS= read -r n; do
        [ -z "$n" ] && continue
        curl -sS -X DELETE "${URL}/storage/v1/object/${BUCKET}/${PREFIX}/${n}" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" >/dev/null 2>&1 || true
    done
    log "Rotación remota: ${drop} copia(s) antiguas eliminadas (se conservan ${KEEP})."
}
prune_remote || true
