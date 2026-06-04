import { Zap, Loader2, Play } from 'lucide-react'
import { useAutomations, useToggleAutomation, useRunAutomation } from '../../hooks/useAutomations'
import { EmptyState } from '../../components/common/EmptyState'
import { cn, timeAgo } from '../../lib/utils'
import type { Automation } from '../../types/automation'

export function AutomationsPage() {
  const { data, isLoading } = useAutomations()
  const automations = data ?? []

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
      </div>
    )
  }

  if (automations.length === 0) {
    return (
      <EmptyState icon={Zap} title="Sin automatizaciones" description="Aún no hay automatizaciones configuradas." />
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {automations.map((a) => (
        <AutomationCard key={a.id} automation={a} />
      ))}
    </div>
  )
}

function AutomationCard({ automation }: { automation: Automation }) {
  const toggle = useToggleAutomation()
  const run = useRunAutomation()
  const successRate =
    automation.execution_count > 0
      ? Math.round(
          (automation.recent_executions.filter((e) => e.status === 'success').length /
            Math.max(automation.recent_executions.length, 1)) *
            100,
        )
      : 0

  return (
    <div className="card-base">
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-warning/10 text-warning">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-medium text-text-primary">{automation.name}</h3>
            <p className="text-xs text-text-secondary">{automation.description}</p>
          </div>
        </div>
        <button
          onClick={() => toggle.mutate({ id: automation.id, is_active: !automation.is_active })}
          className={cn(
            'relative h-6 w-11 rounded-full transition',
            automation.is_active ? 'bg-primary' : 'bg-text-primary/10',
          )}
          aria-label="toggle"
        >
          <span
            className={cn(
              'absolute top-0.5 h-5 w-5 rounded-full bg-white transition',
              automation.is_active ? 'left-[22px]' : 'left-0.5',
            )}
          />
        </button>
      </div>

      <div className="mb-3 grid grid-cols-3 gap-2 text-center">
        <Stat label="Ejecuciones" value={automation.execution_count} />
        <Stat label="Éxito" value={`${successRate}%`} />
        <Stat
          label="Última"
          value={automation.last_executed_at ? timeAgo(automation.last_executed_at) : '—'}
          small
        />
      </div>

      <button
        onClick={() => run.mutate(automation.id)}
        disabled={run.isPending}
        className="flex w-full items-center justify-center gap-2 rounded-lg border border-border py-2 text-sm font-medium text-text-secondary hover:bg-text-primary/5"
      >
        <Play className="h-4 w-4" /> Ejecutar ahora
      </button>
    </div>
  )
}

function Stat({ label, value, small }: { label: string; value: string | number; small?: boolean }) {
  return (
    <div className="rounded-lg bg-background py-2">
      <p className={cn('font-semibold text-text-primary', small ? 'text-xs' : 'text-lg')}>{value}</p>
      <p className="text-[10px] text-text-secondary">{label}</p>
    </div>
  )
}
