import { useQuery } from '@tanstack/react-query'
import { Clock, AlertTriangle } from 'lucide-react'
import { api } from '../../lib/api'

interface TenantMe {
  plan: string
  trial_ends_at: string | null
  payment_state: string
  payment_due_at: string | null
}

/**
 * Aviso de cobro para el negocio. Cubre dos casos:
 *  - Prueba (trial): días restantes de la prueba gratuita.
 *  - Plan pagado: recordatorio cuando la mensualidad está por vencer (≤3 días) o
 *    ya venció (pero aún no suspendida). Si está suspendido, el backend devuelve
 *    402 y el interceptor lleva a /app/upgrade, así que este banner no se muestra.
 */
export function TrialBanner() {
  const { data } = useQuery({
    queryKey: ['tenant-me'],
    queryFn: async () => (await api.get<TenantMe>('/tenants/me')).data,
  })

  if (!data) return null

  const due = data.payment_due_at ?? data.trial_ends_at
  if (!due) return null
  const daysLeft = Math.ceil((new Date(due).getTime() - Date.now()) / (1000 * 60 * 60 * 24))

  const state = data.payment_state
  const isTrial = data.plan === 'trial'

  // No mostrar nada si todo está al día y lejos del vencimiento.
  if (state !== 'due_soon' && state !== 'overdue') {
    if (isTrial && daysLeft > 0) {
      return (
        <Bar urgent={daysLeft <= 3}>
          Tu prueba gratuita termina en{' '}
          <strong>
            {daysLeft} día{daysLeft === 1 ? '' : 's'}
          </strong>. Paga tu primera mensualidad para no perder el servicio.
        </Bar>
      )
    }
    return null
  }

  if (state === 'overdue') {
    return (
      <Bar urgent>
        {isTrial ? 'Tu prueba gratuita terminó' : 'Tu mensualidad venció'}. Paga ya para no perder
        el servicio — tu agente puede ser suspendido en cualquier momento.
      </Bar>
    )
  }

  // due_soon
  return (
    <Bar urgent={daysLeft <= 3}>
      {isTrial ? 'Tu prueba gratuita' : 'Tu mensualidad'} vence en{' '}
      <strong>
        {Math.max(daysLeft, 0)} día{daysLeft === 1 ? '' : 's'}
      </strong>. Paga por adelantado para seguir atendiendo 24/7.
    </Bar>
  )
}

function Bar({ urgent, children }: { urgent: boolean; children: React.ReactNode }) {
  return (
    <div
      className={`flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium ${
        urgent
          ? 'bg-warning/15 text-warning border-b border-warning/30'
          : 'bg-primary/10 text-primary border-b border-primary/20'
      }`}
    >
      {urgent ? (
        <AlertTriangle className="h-4 w-4 flex-shrink-0" />
      ) : (
        <Clock className="h-4 w-4 flex-shrink-0" />
      )}
      <span>{children}</span>
    </div>
  )
}
