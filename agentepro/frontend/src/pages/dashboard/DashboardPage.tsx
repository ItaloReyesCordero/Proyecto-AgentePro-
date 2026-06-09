import { useEffect, useMemo } from 'react'
import { MessageSquare, Users, Phone, Flame, TrendingUp, TrendingDown } from 'lucide-react'
import { motion, animate, useMotionValue, useTransform, useReducedMotion } from 'framer-motion'
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
  Cell,
} from 'recharts'
import { useMetricsSummary } from '../../hooks/useMetrics'
import { useAuthStore } from '../../stores/auth.store'
import { useThemeStore } from '../../stores/theme.store'
import { cn } from '../../lib/utils'
import { ActivationCard } from '../../components/common/ActivationCard'
import { Skeleton } from '../../components/ui/Skeleton'

const FUNNEL_COLORS: Record<string, string> = {
  cold: '#3B82F6',
  warm: '#F59E0B',
  hot: '#EF4444',
  customer: '#10B981',
}

/** Lee el color de marca actual (var --primary) como string rgb() para Recharts. */
function useBrandRgb(): string {
  const mode = useThemeStore((s) => s.mode)
  const brand = useThemeStore((s) => s.brandColor)
  return useMemo(() => {
    const raw = getComputedStyle(document.documentElement)
      .getPropertyValue('--primary')
      .trim()
    return raw ? `rgb(${raw})` : '#10B981'
    // Recalcula cuando cambia el tema o el color de marca.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, brand])
}

/** Número que cuenta de 0 hasta `value` al montar (efecto premium en los KPIs). */
function AnimatedNumber({ value }: { value: number }) {
  const reduce = useReducedMotion()
  const mv = useMotionValue(0)
  const text = useTransform(mv, (v) => Math.round(v).toLocaleString('es-PE'))

  useEffect(() => {
    if (reduce) {
      mv.set(value)
      return
    }
    const controls = animate(mv, value, { duration: 0.9, ease: 'easeOut' })
    return () => controls.stop()
  }, [value, reduce, mv])

  return <motion.span>{text}</motion.span>
}

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06 } },
}
const item = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0 },
}

export function DashboardPage() {
  const { data, isLoading } = useMetricsSummary('7d')
  const user = useAuthStore((s) => s.user)
  const brand = useBrandRgb()

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Buenos días' : hour < 19 ? 'Buenas tardes' : 'Buenas noches'

  const tooltipStyle = {
    background: 'rgb(var(--card))',
    border: '1px solid rgb(var(--border))',
    borderRadius: 8,
    color: 'rgb(var(--text-primary))',
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div
        variants={item}
        className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/15 via-card to-secondary/10 p-6"
      >
        <h2 className="font-heading text-2xl font-bold text-text-primary">
          {greeting}, {user?.full_name?.split(' ')[0] ?? ''} 👋
        </h2>
        <p className="mt-1 text-sm capitalize text-text-secondary">
          {new Date().toLocaleDateString('es-PE', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
          })}
        </p>
      </motion.div>

      <motion.div variants={item}>
        <ActivationCard />
      </motion.div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard
          icon={MessageSquare}
          label="Mensajes hoy"
          value={data?.messages_today ?? 0}
          change={data?.messages_change_pct ?? 0}
          color="text-primary"
          iconBg="bg-primary/10"
          loading={isLoading}
        />
        <KpiCard
          icon={Users}
          label="Leads nuevos"
          value={data?.new_leads ?? 0}
          change={data?.leads_change_pct ?? 0}
          color="text-secondary"
          iconBg="bg-secondary/10"
          loading={isLoading}
        />
        <KpiCard
          icon={Phone}
          label="Llamadas"
          value={data?.total_calls ?? 0}
          color="text-warning"
          iconBg="bg-warning/10"
          loading={isLoading}
        />
        <KpiCard
          icon={Flame}
          label="Leads calientes"
          value={data?.hot_leads_count ?? 0}
          color="text-red-400"
          iconBg="bg-red-400/10"
          loading={isLoading}
        />
      </div>

      <motion.div variants={item} className="card-base">
        <h3 className="mb-4 font-heading font-semibold text-text-primary">
          Volumen de mensajes — últimos 7 días
        </h3>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={data?.message_volume_chart ?? []}>
            <defs>
              <linearGradient id="msgGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={brand} stopOpacity={0.4} />
                <stop offset="95%" stopColor={brand} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" stroke="rgb(var(--text-secondary))" fontSize={11} tickFormatter={(d) => d.slice(5)} />
            <YAxis stroke="rgb(var(--text-secondary))" fontSize={11} allowDecimals={false} />
            <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: 'rgb(var(--text-primary))' }} />
            <Area type="monotone" dataKey="count" stroke={brand} strokeWidth={2} fill="url(#msgGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

      <motion.div variants={item} className="card-base">
        <h3 className="mb-4 font-heading font-semibold text-text-primary">Embudo de leads</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data?.leads_funnel ?? []}>
            <XAxis dataKey="stage" stroke="rgb(var(--text-secondary))" fontSize={11} />
            <YAxis stroke="rgb(var(--text-secondary))" fontSize={11} allowDecimals={false} />
            <Tooltip
              contentStyle={tooltipStyle}
              labelStyle={{ color: 'rgb(var(--text-primary))' }}
              cursor={{ fill: 'rgba(127,127,127,0.08)' }}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {(data?.leads_funnel ?? []).map((entry) => (
                <Cell key={entry.stage} fill={FUNNEL_COLORS[entry.stage] ?? '#6B7280'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </motion.div>
  )
}

interface KpiCardProps {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: number
  change?: number
  color: string
  iconBg: string
  loading: boolean
}

function KpiCard({ icon: Icon, label, value, change, color, iconBg, loading }: KpiCardProps) {
  const positive = (change ?? 0) >= 0

  if (loading) {
    return (
      <motion.div variants={item} className="card-base space-y-3">
        <Skeleton className="h-9 w-9 rounded-lg" />
        <Skeleton className="h-7 w-20" />
        <Skeleton className="h-3 w-24" />
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={item}
      whileHover={{ y: -3 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="card-base transition-shadow hover:shadow-lg hover:shadow-primary/5"
    >
      <div className="mb-3 flex items-center justify-between">
        <div className={cn('flex h-9 w-9 items-center justify-center rounded-lg', iconBg, color)}>
          <Icon className="h-5 w-5" />
        </div>
        {change !== undefined && (
          <span
            className={cn(
              'flex items-center gap-1 text-xs font-medium',
              positive ? 'text-primary' : 'text-red-400',
            )}
          >
            {positive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
      <p className="font-heading text-2xl font-bold tabular-nums text-text-primary">
        <AnimatedNumber value={value} />
      </p>
      <p className="text-xs text-text-secondary">{label}</p>
    </motion.div>
  )
}
