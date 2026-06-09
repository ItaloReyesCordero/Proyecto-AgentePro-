import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Database, Loader2, RefreshCw, Link2, Unlink } from 'lucide-react'
import { api, apiErrorMessage } from '../../lib/api'
import { useUIStore } from '../../stores/ui.store'

interface NotionStatus {
  connected: boolean
  database_id: string | null
  last_synced_at: string | null
  services_count: number
}

interface SyncResult {
  synced: number
  last_synced_at: string | null
}

export function NotionSettings() {
  const qc = useQueryClient()
  const addToast = useUIStore((s) => s.addToast)
  const [apiKey, setApiKey] = useState('')
  const [databaseId, setDatabaseId] = useState('')

  const { data: status, isLoading } = useQuery({
    queryKey: ['notion-status'],
    queryFn: async () => (await api.get<NotionStatus>('/notion/status')).data,
    retry: false,
  })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['notion-status'] })
    qc.invalidateQueries({ queryKey: ['agent-config'] })
  }

  const connect = useMutation({
    mutationFn: async () =>
      (await api.post<SyncResult>('/notion/connect', { api_key: apiKey, database_id: databaseId })).data,
    onSuccess: (r) => {
      addToast({ title: `Notion conectado: ${r.synced} servicios sincronizados`, variant: 'success' })
      setApiKey('')
      invalidate()
    },
    onError: (e) => addToast({ title: apiErrorMessage(e, 'No se pudo conectar Notion'), variant: 'error' }),
  })

  const sync = useMutation({
    mutationFn: async () => (await api.post<SyncResult>('/notion/sync', {})).data,
    onSuccess: (r) => {
      addToast({ title: `Sincronizado: ${r.synced} servicios`, variant: 'success' })
      invalidate()
    },
    onError: (e) => addToast({ title: apiErrorMessage(e, 'No se pudo sincronizar'), variant: 'error' }),
  })

  const disconnect = useMutation({
    mutationFn: async () => (await api.post('/notion/disconnect', {})).data,
    onSuccess: () => {
      addToast({ title: 'Notion desconectado', variant: 'default' })
      invalidate()
    },
    onError: (e) => addToast({ title: apiErrorMessage(e, 'No se pudo desconectar'), variant: 'error' }),
  })

  return (
    <section className="card-base space-y-3">
      <div className="flex items-center gap-2">
        <Database className="h-5 w-5 text-primary" />
        <h3 className="font-heading font-semibold text-text-primary">CRM en Notion</h3>
      </div>
      <p className="text-sm text-text-secondary">
        Conecta una base de datos de Notion con tus servicios y precios. El agente leerá
        ese catálogo para responder. Crea una integración en{' '}
        <a
          href="https://www.notion.so/my-integrations"
          target="_blank"
          rel="noreferrer"
          className="text-primary underline"
        >
          notion.so/my-integrations
        </a>, comparte la base con ella, y pega aquí el token y el ID de la base.
      </p>

      {isLoading ? (
        <div className="flex justify-center py-4">
          <Loader2 className="h-5 w-5 animate-spin text-text-secondary" />
        </div>
      ) : status?.connected ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-border/50 pb-2 text-sm">
            <span className="text-text-secondary">Estado</span>
            <span className="font-medium text-success">Conectado</span>
          </div>
          <div className="flex items-center justify-between border-b border-border/50 pb-2 text-sm">
            <span className="text-text-secondary">Servicios sincronizados</span>
            <span className="font-medium text-text-primary">{status.services_count}</span>
          </div>
          <div className="flex items-center justify-between border-b border-border/50 pb-2 text-sm">
            <span className="text-text-secondary">Última sincronización</span>
            <span className="font-medium text-text-primary">
              {status.last_synced_at ? new Date(status.last_synced_at).toLocaleString() : '—'}
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => sync.mutate()}
              disabled={sync.isPending}
              className="btn-primary flex items-center gap-2 text-sm"
            >
              {sync.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Sincronizar ahora
            </button>
            <button
              onClick={() => disconnect.mutate()}
              disabled={disconnect.isPending}
              className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm text-text-secondary hover:text-error"
            >
              <Unlink className="h-4 w-4" />
              Desconectar
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <label htmlFor="notion-api-key" className="mb-1 block text-sm font-medium text-text-secondary">Token de integración (Notion)</label>
            <input
              id="notion-api-key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="secret_xxx o ntn_xxx"
              className="input-base w-full"
            />
          </div>
          <div>
            <label htmlFor="notion-database-id" className="mb-1 block text-sm font-medium text-text-secondary">ID o enlace de la base de datos</label>
            <input
              id="notion-database-id"
              type="text"
              value={databaseId}
              onChange={(e) => setDatabaseId(e.target.value)}
              placeholder="https://notion.so/...  o  el ID de 32 caracteres"
              className="input-base w-full"
            />
          </div>
          <button
            onClick={() => connect.mutate()}
            disabled={connect.isPending || !apiKey.trim() || !databaseId.trim()}
            className="btn-primary flex items-center gap-2 text-sm disabled:opacity-50"
          >
            {connect.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Link2 className="h-4 w-4" />}
            Conectar y sincronizar
          </button>
        </div>
      )}
    </section>
  )
}
