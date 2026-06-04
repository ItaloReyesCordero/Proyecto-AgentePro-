import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  CalendarCheck,
  Loader2,
  Check,
  X,
  Plus,
  MessageSquare,
  Phone,
  Instagram,
  Pencil,
} from 'lucide-react'
import { api, apiErrorMessage } from '../../lib/api'
import { EmptyState } from '../../components/common/EmptyState'
import { useUIStore } from '../../stores/ui.store'

interface Appointment {
  id: string
  customer_name: string | null
  customer_phone: string | null
  service_name: string | null
  scheduled_at: string | null
  raw_when: string | null
  notes: string | null
  status: string
  source: string
  created_at: string
}

const STATUS_LABEL: Record<string, string> = {
  requested: 'Solicitada',
  confirmed: 'Confirmada',
  cancelled: 'Cancelada',
  completed: 'Completada',
}
const STATUS_CLASS: Record<string, string> = {
  requested: 'bg-warning/15 text-warning',
  confirmed: 'bg-secondary/15 text-secondary',
  cancelled: 'bg-error/15 text-error',
  completed: 'bg-success/15 text-success',
}
const SOURCE_ICON: Record<string, React.ComponentType<{ className?: string }>> = {
  whatsapp: MessageSquare,
  instagram: Instagram,
  voice: Phone,
  manual: Pencil,
}

function formatWhen(a: Appointment): string {
  if (a.scheduled_at) return new Date(a.scheduled_at).toLocaleString('es-PE', {
    weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
  })
  return a.raw_when || 'Por coordinar'
}

export function AppointmentsPage() {
  const qc = useQueryClient()
  const addToast = useUIStore((s) => s.addToast)
  const [showForm, setShowForm] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: async () => (await api.get<Appointment[]>('/appointments')).data,
  })
  const appts = data ?? []

  const setStatus = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) =>
      (await api.patch(`/appointments/${id}`, { status })).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['appointments'] })
    },
    onError: (e) => addToast({ title: apiErrorMessage(e, 'No se pudo actualizar'), variant: 'error' }),
  })

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-heading text-xl font-semibold text-text-primary">Citas</h2>
          <p className="text-sm text-text-secondary">
            Citas detectadas por el agente (WhatsApp, Instagram, llamadas) y las que agregues a mano.
          </p>
        </div>
        <button onClick={() => setShowForm((v) => !v)} className="btn-primary flex items-center gap-2 text-sm">
          <Plus className="h-4 w-4" /> Nueva cita
        </button>
      </div>

      {showForm && <NewAppointmentForm onClose={() => setShowForm(false)} />}

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
        </div>
      ) : appts.length === 0 ? (
        <EmptyState
          icon={CalendarCheck}
          title="Aún no hay citas"
          description="Cuando un cliente pida una cita por WhatsApp o teléfono, aparecerá aquí y te avisaremos."
        />
      ) : (
        <div className="space-y-2">
          {appts.map((a) => {
            const SourceIcon = SOURCE_ICON[a.source] ?? CalendarCheck
            return (
              <div key={a.id} className="card-base flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <SourceIcon className="h-5 w-5 text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-text-primary">
                    {a.service_name || 'Cita'} · {a.customer_name || a.customer_phone || 'Cliente'}
                  </p>
                  <p className="text-xs text-text-secondary">
                    {formatWhen(a)}
                    {a.customer_phone ? ` · ${a.customer_phone}` : ''}
                  </p>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_CLASS[a.status] ?? ''}`}>
                  {STATUS_LABEL[a.status] ?? a.status}
                </span>
                {(a.status === 'requested' || a.status === 'confirmed') && (
                  <div className="flex gap-1">
                    {a.status === 'requested' && (
                      <button
                        title="Confirmar"
                        onClick={() => setStatus.mutate({ id: a.id, status: 'confirmed' })}
                        className="rounded-lg border border-border p-1.5 text-secondary hover:bg-secondary/10"
                      >
                        <Check className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      title="Marcar completada"
                      onClick={() => setStatus.mutate({ id: a.id, status: 'completed' })}
                      className="rounded-lg border border-border p-1.5 text-success hover:bg-success/10"
                    >
                      <CalendarCheck className="h-4 w-4" />
                    </button>
                    <button
                      title="Cancelar"
                      onClick={() => setStatus.mutate({ id: a.id, status: 'cancelled' })}
                      className="rounded-lg border border-border p-1.5 text-error hover:bg-error/10"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function NewAppointmentForm({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const addToast = useUIStore((s) => s.addToast)
  const [form, setForm] = useState({ customer_name: '', customer_phone: '', service_name: '', scheduled_at: '' })

  const create = useMutation({
    mutationFn: async () => {
      const payload: Record<string, unknown> = {
        customer_name: form.customer_name || null,
        customer_phone: form.customer_phone || null,
        service_name: form.service_name || null,
        scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : null,
      }
      return (await api.post('/appointments', payload)).data
    },
    onSuccess: () => {
      addToast({ title: 'Cita creada', variant: 'success' })
      qc.invalidateQueries({ queryKey: ['appointments'] })
      onClose()
    },
    onError: (e) => addToast({ title: apiErrorMessage(e, 'No se pudo crear'), variant: 'error' }),
  })

  return (
    <div className="card-base space-y-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <input className="input-base" placeholder="Nombre del cliente"
          value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} />
        <input className="input-base" placeholder="Teléfono (+51...)"
          value={form.customer_phone} onChange={(e) => setForm({ ...form, customer_phone: e.target.value })} />
        <input className="input-base" placeholder="Servicio"
          value={form.service_name} onChange={(e) => setForm({ ...form, service_name: e.target.value })} />
        <input className="input-base" type="datetime-local"
          value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} />
      </div>
      <div className="flex gap-2">
        <button onClick={() => create.mutate()} disabled={create.isPending} className="btn-primary text-sm">
          {create.isPending ? 'Guardando...' : 'Guardar cita'}
        </button>
        <button onClick={onClose} className="rounded-lg border border-border px-3 py-2 text-sm text-text-secondary">
          Cancelar
        </button>
      </div>
    </div>
  )
}
