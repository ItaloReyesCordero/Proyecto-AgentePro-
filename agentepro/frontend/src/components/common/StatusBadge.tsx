import { cn } from '../../lib/utils'
import type { ConversationStatus, LeadStage, CallOutcome } from '../../types'

type BadgeVariant =
  | ConversationStatus
  | LeadStage
  | CallOutcome
  | 'positive'
  | 'neutral'
  | 'negative'
  | 'published'
  | 'scheduled'
  | 'pending_approval'
  | 'draft'
  | 'rejected'

const BADGE_CONFIG: Record<string, { label: string; className: string }> = {
  // Conversation status
  open: { label: 'Abierta', className: 'bg-primary/10 text-primary border-primary/20' },
  human_takeover: { label: 'Agente humano', className: 'bg-secondary/10 text-secondary border-secondary/20' },
  closed: { label: 'Cerrada', className: 'bg-gray-500/10 text-gray-400 border-gray-500/20' },
  waiting: { label: 'En espera', className: 'bg-warning/10 text-warning border-warning/20' },
  bot_paused: { label: 'Bot pausado', className: 'bg-orange-500/10 text-orange-400 border-orange-500/20' },
  // Lead stages
  cold: { label: 'Frio', className: 'bg-blue-400/10 text-blue-400 border-blue-400/20' },
  warm: { label: 'Tibio', className: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20' },
  hot: { label: 'Caliente', className: 'bg-red-400/10 text-red-400 border-red-400/20' },
  customer: { label: 'Cliente', className: 'bg-primary/10 text-primary border-primary/20' },
  lost: { label: 'Perdido', className: 'bg-gray-500/10 text-gray-400 border-gray-500/20' },
  // Call outcomes
  appointment_booked: { label: 'Cita agendada', className: 'bg-primary/10 text-primary border-primary/20' },
  info_provided: { label: 'Info brindada', className: 'bg-secondary/10 text-secondary border-secondary/20' },
  escalated: { label: 'Escalado', className: 'bg-orange-500/10 text-orange-400 border-orange-500/20' },
  follow_up_needed: { label: 'Seguimiento', className: 'bg-warning/10 text-warning border-warning/20' },
  sale: { label: 'Venta', className: 'bg-primary/10 text-primary border-primary/20' },
  no_interest: { label: 'Sin interés', className: 'bg-gray-500/10 text-gray-400 border-gray-500/20' },
  // Sentiment
  positive: { label: 'Positivo', className: 'bg-primary/10 text-primary border-primary/20' },
  neutral: { label: 'Neutral', className: 'bg-gray-500/10 text-gray-400 border-gray-500/20' },
  negative: { label: 'Negativo', className: 'bg-red-400/10 text-red-400 border-red-400/20' },
  // Instagram post status
  published: { label: 'Publicado', className: 'bg-primary/10 text-primary border-primary/20' },
  scheduled: { label: 'Programado', className: 'bg-secondary/10 text-secondary border-secondary/20' },
  pending_approval: { label: 'Pendiente', className: 'bg-warning/10 text-warning border-warning/20' },
  draft: { label: 'Borrador', className: 'bg-gray-500/10 text-gray-400 border-gray-500/20' },
  rejected: { label: 'Rechazado', className: 'bg-red-400/10 text-red-400 border-red-400/20' },
}

interface StatusBadgeProps {
  status: BadgeVariant
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = BADGE_CONFIG[status] ?? {
    label: status,
    className: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
        config.className,
        className,
      )}
    >
      {config.label}
    </span>
  )
}
