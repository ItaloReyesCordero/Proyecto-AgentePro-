import { useState } from 'react'
import { Phone, PhoneIncoming, PhoneOutgoing, Loader2 } from 'lucide-react'
import { useCalls, useCall } from '../../hooks/useCalls'
import { StatusBadge } from '../../components/common/StatusBadge'
import { EmptyState } from '../../components/common/EmptyState'
import { cn, formatDuration, timeAgo } from '../../lib/utils'

const SENTIMENT_EMOJI: Record<string, string> = {
  positive: '😊',
  neutral: '😐',
  negative: '😟',
}

export function CallsPage() {
  const { data, isLoading } = useCalls()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const calls = data?.items ?? []

  return (
    <div className="flex h-[calc(100vh-7rem)] gap-4">
      <div className="flex w-1/2 flex-col overflow-hidden rounded-2xl border border-border bg-card">
        <div className="border-b border-border px-4 py-3">
          <h3 className="font-heading font-semibold text-text-primary">Llamadas</h3>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="h-5 w-5 animate-spin text-text-secondary" />
            </div>
          ) : calls.length === 0 ? (
            <EmptyState icon={Phone} title="Sin llamadas" description="Aún no hay llamadas registradas." />
          ) : (
            calls.map((call) => (
              <button
                key={call.id}
                onClick={() => setSelectedId(call.id)}
                className={cn(
                  'flex w-full items-center gap-3 border-b border-border/50 px-4 py-3 text-left transition hover:bg-text-primary/5',
                  selectedId === call.id && 'bg-text-primary/5',
                )}
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-text-primary/5">
                  {call.direction === 'inbound' ? (
                    <PhoneIncoming className="h-4 w-4 text-secondary" />
                  ) : (
                    <PhoneOutgoing className="h-4 w-4 text-primary" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-text-primary">
                    {call.contact?.name ?? call.from_number}
                  </p>
                  <p className="text-xs text-text-secondary">
                    {formatDuration(call.duration_seconds)} · {timeAgo(call.created_at)}
                  </p>
                </div>
                {call.outcome && <StatusBadge status={call.outcome} />}
                {call.summary && <span>{SENTIMENT_EMOJI[call.summary.sentiment] ?? ''}</span>}
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 overflow-hidden rounded-2xl border border-border bg-card">
        {selectedId ? (
          <CallDetail callId={selectedId} />
        ) : (
          <EmptyState
            icon={Phone}
            title="Selecciona una llamada"
            description="Verás la transcripción y el resumen generado por IA."
            className="m-auto h-full"
          />
        )}
      </div>
    </div>
  )
}

function CallDetail({ callId }: { callId: string }) {
  const { data: call, isLoading } = useCall(callId)
  if (isLoading || !call) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-5 w-5 animate-spin text-text-secondary" />
      </div>
    )
  }
  return (
    <div className="h-full overflow-y-auto scrollbar-thin p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="font-heading text-lg font-semibold text-text-primary">
            {call.contact?.name ?? call.from_number}
          </h3>
          <p className="text-sm text-text-secondary">
            {call.direction === 'inbound' ? 'Entrante' : 'Saliente'} ·{' '}
            {formatDuration(call.duration_seconds)}
          </p>
        </div>
        {call.outcome && <StatusBadge status={call.outcome} />}
      </div>

      {call.recording_url && (
        <audio controls src={call.recording_url} className="mb-4 w-full" />
      )}

      {call.summary && (
        <div className="card-base mb-4">
          <h4 className="mb-2 font-medium text-text-primary">Resumen IA</h4>
          {call.ai_summary && <p className="mb-3 text-sm text-text-secondary">{call.ai_summary}</p>}
          {call.summary.key_points.length > 0 && (
            <ul className="list-inside list-disc space-y-1 text-sm text-text-secondary">
              {call.summary.key_points.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="card-base">
        <h4 className="mb-2 font-medium text-text-primary">Transcripción</h4>
        <p className="whitespace-pre-wrap text-sm text-text-secondary">
          {call.transcript ?? 'Transcripción no disponible.'}
        </p>
      </div>
    </div>
  )
}
