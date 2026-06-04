import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Loader2,
  Building2,
  Users,
  DollarSign,
  TrendingUp,
  RotateCcw,
  TrendingDown,
  ShieldCheck,
  Plus,
  Download,
  Trash2,
  Search,
  ScrollText,
  X,
  Wallet,
  Clock,
  KeyRound,
  Copy,
  Check,
  CalendarClock,
  BadgeCheck,
  Ban,
  LayoutDashboard,
  Activity,
  Phone,
  PhoneCall,
  MessageSquare,
  Power,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useState } from 'react'
import { api, apiErrorMessage } from '../../lib/api'

interface TenantStat {
  id: string
  name: string
  plan: string
  is_active: boolean
  contacts: number
  messages: number
  calls: number
  call_seconds: number
  conversations: number
  tokens_used: number
  claude_usd: number
  voice_usd: number
  whatsapp_usd: number
  cost_usd: number
  cost_pen: number
  revenue_pen: number
  profit_pen: number
}
interface Analytics {
  totals: {
    total_tenants: number
    active_paid_tenants: number
    trial_tenants: number
    mrr_pen: number
    real_cost_pen_total: number
    est_monthly_profit_pen: number
    claude_usd_total: number
    total_messages: number
    total_calls: number
  }
  by_plan: Record<string, number>
  tenants: TenantStat[]
  monthly: { month: string; messages: number; calls: number; claude_usd: number }[]
}

interface Tenant {
  id: string
  name: string
  slug: string
  business_type: string
  plan: string
  is_active: boolean
}

type Health = Record<string, boolean>

interface ResetRequest {
  id: string
  email: string
  user_id: string | null
  tenant_id: string | null
  tenant_name: string | null
  full_name: string | null
  status: string
  created_at: string
}
interface ResetResult {
  user_email: string
  new_password: string
}
interface BillingPending {
  id: string
  name: string
  plan: string
  payment_state: 'due_soon' | 'overdue' | 'suspended'
  due_at: string | null
  days_overdue: number
  amount_pen: number
  is_active: boolean
}

type TabKey = 'dashboard' | 'negocios' | 'uso' | 'cobros' | 'recuperacion'

const PLANS = ['trial', 'inicial', 'basic', 'professional', 'enterprise']
const PLAN_COLORS: Record<string, string> = {
  trial: '#6B7280',
  inicial: '#F59E0B',
  basic: '#3B82F6',
  professional: '#10B981',
  enterprise: '#A855F7',
}
const BUSINESS_TYPES = ['healthcare', 'education', 'retail', 'ecommerce', 'restaurant', 'real_estate', 'services', 'other']
const EMPTY_FORM = {
  business_name: '',
  business_type: 'services',
  owner_name: '',
  owner_email: '',
  owner_phone: '',
  plan: 'trial',
  password: '',
}
const soles = (n: number) => `S/ ${n.toLocaleString('es-PE', { maximumFractionDigits: 0 })}`

export function AdminPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<TabKey>('dashboard')
  const [notice, setNotice] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ ...EMPTY_FORM })
  const [search, setSearch] = useState('')
  const [logsTenant, setLogsTenant] = useState<Tenant | null>(null)
  const [resetResult, setResetResult] = useState<ResetResult | null>(null)

  const analytics = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: async () => (await api.get<Analytics>('/admin/analytics')).data,
  })
  const health = useQuery({
    queryKey: ['admin-health'],
    queryFn: async () => (await api.get<Health>('/admin/health')).data,
  })
  const tenants = useQuery({
    queryKey: ['admin-tenants'],
    queryFn: async () => (await api.get<Tenant[]>('/admin/tenants')).data,
  })
  const resetRequests = useQuery({
    queryKey: ['admin-reset-requests'],
    queryFn: async () => (await api.get<ResetRequest[]>('/admin/password-reset-requests')).data,
    refetchInterval: 30000,
  })
  const billing = useQuery({
    queryKey: ['admin-billing-pending'],
    queryFn: async () => (await api.get<BillingPending[]>('/admin/billing/pending')).data,
    refetchInterval: 30000,
  })

  function refresh() {
    qc.invalidateQueries({ queryKey: ['admin-tenants'] })
    qc.invalidateQueries({ queryKey: ['admin-analytics'] })
    qc.invalidateQueries({ queryKey: ['admin-billing-pending'] })
  }

  const confirmPayment = useMutation({
    mutationFn: async (tenantId: string) =>
      (await api.post(`/admin/tenants/${tenantId}/confirm-payment`, {})).data,
    onSuccess: () => {
      setNotice('Pago confirmado. Se reactivó el servicio y se movió el vencimiento un mes.')
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e, 'No se pudo confirmar el pago')),
  })
  const suspendBilling = useMutation({
    mutationFn: async (tenantId: string) =>
      (await api.post(`/admin/tenants/${tenantId}/suspend-billing`)).data,
    onSuccess: () => {
      setNotice('Negocio suspendido por falta de pago. Su panel quedó bloqueado.')
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e, 'No se pudo suspender')),
  })

  const approveReset = useMutation({
    mutationFn: async (requestId: string) =>
      (await api.post<ResetResult>(`/admin/password-reset-requests/${requestId}/approve`)).data,
    onSuccess: (data) => {
      setResetResult(data)
      qc.invalidateQueries({ queryKey: ['admin-reset-requests'] })
    },
    onError: (e) => setNotice(apiErrorMessage(e, 'No se pudo restablecer la contraseña')),
  })
  const dismissReset = useMutation({
    mutationFn: async (requestId: string) =>
      (await api.delete(`/admin/password-reset-requests/${requestId}`)).data,
    onSuccess: () => {
      setNotice('Solicitud descartada.')
      qc.invalidateQueries({ queryKey: ['admin-reset-requests'] })
    },
    onError: (e) => setNotice(apiErrorMessage(e)),
  })
  const resetOwner = useMutation({
    mutationFn: async (tenantId: string) =>
      (await api.post<ResetResult>(`/admin/tenants/${tenantId}/reset-owner-password`)).data,
    onSuccess: (data) => {
      setResetResult(data)
      qc.invalidateQueries({ queryKey: ['admin-reset-requests'] })
    },
    onError: (e) => setNotice(apiErrorMessage(e, 'No se pudo restablecer la contraseña')),
  })

  const resetUsage = useMutation({
    mutationFn: async () => (await api.post('/admin/reset-usage')).data,
    onSuccess: () => {
      setNotice('Uso mensual reiniciado para todos los negocios.')
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e)),
  })
  const patchTenant = useMutation({
    mutationFn: async ({ id, body }: { id: string; body: Partial<Tenant> }) =>
      (await api.patch<Tenant>(`/admin/tenants/${id}`, body)).data,
    onSuccess: (_d, vars) => {
      setNotice(
        'is_active' in vars.body
          ? vars.body.is_active
            ? 'Negocio activado. Su agente y panel vuelven a funcionar.'
            : 'Negocio desactivado. Su agente dejó de responder y su panel quedó bloqueado.'
          : 'Negocio actualizado.',
      )
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e)),
  })
  const createTenant = useMutation({
    mutationFn: async () => (await api.post<Tenant>('/admin/tenants', form)).data,
    onSuccess: (t) => {
      setNotice(`Negocio "${t.name}" creado.`)
      setShowCreate(false)
      setForm({ ...EMPTY_FORM })
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e, 'No se pudo crear el negocio')),
  })
  const deleteTenant = useMutation({
    mutationFn: async (id: string) => (await api.delete(`/admin/tenants/${id}`)).data,
    onSuccess: () => {
      setNotice('Negocio eliminado con todos sus datos.')
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e)),
  })
  const provisionVoice = useMutation({
    mutationFn: async (id: string) =>
      (await api.post<{ retell_agent_id: string; twilio_phone_number: string | null }>(
        `/admin/tenants/${id}/provision-voice`,
      )).data,
    onSuccess: (data) => {
      setNotice(
        `Voz reconectada: agente Retell ${data.retell_agent_id}` +
          (data.twilio_phone_number ? ` · número ${data.twilio_phone_number}` : ' (sin número Twilio: cómpralo aparte)'),
      )
      refresh()
    },
    onError: (e) => setNotice(apiErrorMessage(e, 'No se pudo reconectar la voz')),
  })

  async function exportTenant(t: Tenant) {
    try {
      const data = (await api.get(`/admin/tenants/${t.id}/export`)).data
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${t.slug}-export.json`
      a.click()
      URL.revokeObjectURL(url)
      setNotice(`Datos de "${t.name}" exportados.`)
    } catch (e) {
      setNotice(apiErrorMessage(e, 'No se pudo exportar'))
    }
  }

  function updateForm(field: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const totals = analytics.data?.totals
  const revenueByPlan = ['inicial', 'basic', 'professional', 'enterprise'].map((plan) => ({
    plan,
    revenue: (analytics.data?.tenants ?? [])
      .filter((t) => t.plan === plan && t.is_active)
      .reduce((s, t) => s + t.revenue_pen, 0),
  }))

  const q = search.trim().toLowerCase()
  const visibleTenants = (tenants.data ?? []).filter(
    (t) => !q || t.name.toLowerCase().includes(q) || t.slug.toLowerCase().includes(q),
  )

  const billingCount = billing.data?.length ?? 0
  const resetCount = resetRequests.data?.length ?? 0

  const TABS: { key: TabKey; label: string; icon: React.ComponentType<{ className?: string }>; badge?: number }[] = [
    { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { key: 'negocios', label: 'Negocios', icon: Building2 },
    { key: 'uso', label: 'Uso y consumo', icon: Activity },
    { key: 'cobros', label: 'Cobros', icon: Wallet, badge: billingCount },
    { key: 'recuperacion', label: 'Recuperación', icon: KeyRound, badge: resetCount },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-6 w-6 text-primary" />
        <h2 className="font-heading text-xl font-bold text-text-primary">Panel del fundador</h2>
      </div>

      {/* Navegación por módulos */}
      <div className="flex flex-wrap gap-1.5 border-b border-border pb-px">
        {TABS.map((t) => {
          const active = tab === t.key
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-2 rounded-t-lg px-4 py-2.5 text-sm font-semibold transition ${
                active
                  ? 'border-b-2 border-primary bg-primary/5 text-primary'
                  : 'border-b-2 border-transparent text-text-secondary hover:bg-text-primary/5 hover:text-text-primary'
              }`}
            >
              <t.icon className="h-4 w-4" />
              {t.label}
              {t.badge ? (
                <span className="rounded-full bg-warning/20 px-1.5 py-0.5 text-xs font-bold text-warning">
                  {t.badge}
                </span>
              ) : null}
            </button>
          )
        })}
      </div>

      {notice && (
        <div className="flex items-start justify-between gap-3 rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary">
          <span>{notice}</span>
          <button onClick={() => setNotice(null)} className="text-primary/70 hover:text-primary">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* ───────────────── DASHBOARD ───────────────── */}
      {tab === 'dashboard' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
            <Kpi icon={Wallet} label="Ingreso mensual (MRR)" value={totals ? soles(totals.mrr_pen) : undefined} accent />
            <Kpi icon={TrendingUp} label="Ganancia real/mes" value={totals ? soles(totals.est_monthly_profit_pen) : undefined} accent />
            <Kpi icon={Building2} label="Clientes de pago" value={totals?.active_paid_tenants} />
            <Kpi icon={Clock} label="En prueba" value={totals?.trial_tenants} />
            <Kpi icon={DollarSign} label="Costo Claude (real)" value={totals ? `$${totals.claude_usd_total}` : undefined} />
            <Kpi icon={Users} label="Mensajes totales" value={totals?.total_messages} />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <section className="card-base lg:col-span-2">
              <h3 className="mb-4 font-heading font-semibold text-text-primary">
                Actividad por mes (mensajes y llamadas)
              </h3>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={analytics.data?.monthly ?? []}>
                  <defs>
                    <linearGradient id="m" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="c" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="month" stroke="#9CA3AF" fontSize={11} />
                  <YAxis stroke="#9CA3AF" fontSize={11} allowDecimals={false} />
                  <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', borderRadius: 8 }} labelStyle={{ color: '#F9FAFB' }} />
                  <Area type="monotone" dataKey="messages" name="Mensajes" stroke="#10B981" strokeWidth={2} fill="url(#m)" />
                  <Area type="monotone" dataKey="calls" name="Llamadas" stroke="#F59E0B" strokeWidth={2} fill="url(#c)" />
                </AreaChart>
              </ResponsiveContainer>
            </section>

            <section className="card-base">
              <h3 className="mb-4 font-heading font-semibold text-text-primary">Ingreso por plan (S/ /mes)</h3>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={revenueByPlan}>
                  <XAxis dataKey="plan" stroke="#9CA3AF" fontSize={11} />
                  <YAxis stroke="#9CA3AF" fontSize={11} />
                  <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', borderRadius: 8 }} labelStyle={{ color: '#F9FAFB' }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                  <Bar dataKey="revenue" name="Ingreso S/" radius={[6, 6, 0, 0]}>
                    {revenueByPlan.map((r) => (
                      <Cell key={r.plan} fill={PLAN_COLORS[r.plan] ?? '#6B7280'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </section>
          </div>

          <section className="card-base">
            <h3 className="mb-3 font-heading font-semibold text-text-primary">Estado de servicios (API keys conectadas)</h3>
            <div className="flex flex-wrap gap-2">
              {health.isLoading && <Loader2 className="h-4 w-4 animate-spin text-text-secondary" />}
              {health.data &&
                Object.entries(health.data).map(([name, ok]) => (
                  <span
                    key={name}
                    className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                      ok ? 'border border-primary/30 bg-primary/10 text-primary' : 'border border-border bg-background text-text-secondary'
                    }`}
                  >
                    {name} {ok ? '✓' : '—'}
                  </span>
                ))}
            </div>
            <p className="mt-3 text-xs text-text-secondary">
              ✓ = la API key está configurada en el backend. — = falta configurarla (ese servicio no funcionará).
            </p>
          </section>
        </div>
      )}

      {/* ───────────────── NEGOCIOS ───────────────── */}
      {tab === 'negocios' && (
        <section className="card-base">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-heading font-semibold text-text-primary">Negocios registrados</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowCreate((s) => !s)}
                className="flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary/90"
              >
                <Plus className="h-3.5 w-3.5" />
                Crear negocio
              </button>
              <button
                onClick={() => resetUsage.mutate()}
                disabled={resetUsage.isPending}
                className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-semibold text-text-secondary transition hover:bg-text-primary/5 disabled:opacity-60"
              >
                {resetUsage.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RotateCcw className="h-3.5 w-3.5" />}
                Reiniciar uso mensual
              </button>
            </div>
          </div>

          {showCreate && (
            <form
              onSubmit={(e) => {
                e.preventDefault()
                createTenant.mutate()
              }}
              className="mb-4 grid grid-cols-1 gap-3 rounded-xl border border-border bg-background/50 p-4 md:grid-cols-2"
            >
              <Input label="Nombre del negocio" value={form.business_name} onChange={(v) => updateForm('business_name', v)} required />
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Tipo</label>
                <select value={form.business_type} onChange={(e) => updateForm('business_type', e.target.value)} className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm text-text-primary outline-none focus:border-primary">
                  {BUSINESS_TYPES.map((b) => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
              <Input label="Nombre del dueño" value={form.owner_name} onChange={(v) => updateForm('owner_name', v)} required />
              <Input label="Email del dueño" type="email" value={form.owner_email} onChange={(v) => updateForm('owner_email', v)} required />
              <Input label="Teléfono del dueño" value={form.owner_phone} onChange={(v) => updateForm('owner_phone', v)} required />
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Plan</label>
                <select value={form.plan} onChange={(e) => updateForm('plan', e.target.value)} className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm text-text-primary outline-none focus:border-primary">
                  {PLANS.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <Input label="Contraseña inicial (mín. 6)" type="password" value={form.password} onChange={(v) => updateForm('password', v)} required />
              <div className="flex items-end gap-2">
                <button type="submit" disabled={createTenant.isPending} className="flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary/90 disabled:opacity-60">
                  {createTenant.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                  Crear
                </button>
                <button type="button" onClick={() => setShowCreate(false)} className="rounded-lg border border-border px-4 py-2 text-sm font-semibold text-text-secondary hover:bg-text-primary/5">
                  Cancelar
                </button>
              </div>
            </form>
          )}

          <div className="relative mb-3 max-w-sm">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar negocio por nombre o slug..."
              className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-3 text-sm text-text-primary outline-none focus:border-primary"
            />
          </div>

          {tenants.isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-text-secondary">
                  <tr className="border-b border-border">
                    <th className="py-2 pr-3">Negocio</th>
                    <th className="py-2 pr-3">Plan</th>
                    <th className="py-2 pr-3">Estado</th>
                    <th className="py-2 pr-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleTenants.map((t) => (
                    <tr key={t.id} className="border-b border-border/50">
                      <td className="py-2.5 pr-3">
                        <div className="font-medium text-text-primary">{t.name}</div>
                        <div className="text-xs text-text-secondary">{t.business_type} · {t.slug}</div>
                      </td>
                      <td className="py-2.5 pr-3">
                        <select
                          value={t.plan}
                          onChange={(e) => patchTenant.mutate({ id: t.id, body: { plan: e.target.value } })}
                          className="rounded-md border border-border bg-background px-2 py-1 text-xs text-text-primary outline-none focus:border-primary"
                        >
                          {PLANS.map((p) => <option key={p} value={p}>{p}</option>)}
                        </select>
                      </td>
                      <td className="py-2.5 pr-3">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${t.is_active ? 'bg-primary/10 text-primary' : 'bg-red-500/10 text-red-400'}`}>
                          {t.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3">
                        <div className="flex items-center gap-1.5">
                          <button
                            onClick={() => {
                              const msg = t.is_active
                                ? `¿Desactivar "${t.name}"? Su agente dejará de responder y su panel quedará bloqueado.`
                                : `¿Activar "${t.name}"? Volverá a funcionar normalmente.`
                              if (window.confirm(msg)) {
                                patchTenant.mutate({ id: t.id, body: { is_active: !t.is_active } })
                              }
                            }}
                            disabled={patchTenant.isPending}
                            className={`flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs font-semibold transition disabled:opacity-60 ${
                              t.is_active
                                ? 'border-red-500/30 text-red-400 hover:bg-red-500/10'
                                : 'border-primary/30 text-primary hover:bg-primary/10'
                            }`}
                          >
                            <Power className="h-3.5 w-3.5" />
                            {t.is_active ? 'Desactivar' : 'Activar'}
                          </button>
                          <button title="Ver logs de webhooks" onClick={() => setLogsTenant(t)} className="rounded-md border border-border p-1.5 text-text-secondary transition hover:bg-text-primary/5">
                            <ScrollText className="h-3.5 w-3.5" />
                          </button>
                          <button
                            title="Restablecer contraseña del dueño"
                            onClick={() => {
                              if (window.confirm(`¿Generar una contraseña nueva para el dueño de "${t.name}"? Tendrás que entregársela.`)) {
                                resetOwner.mutate(t.id)
                              }
                            }}
                            className="rounded-md border border-border p-1.5 text-text-secondary transition hover:bg-text-primary/5"
                          >
                            <KeyRound className="h-3.5 w-3.5" />
                          </button>
                          <button
                            title="Reconectar voz (crea un agente de Retell nuevo para este negocio, sin borrar datos)"
                            onClick={() => {
                              if (
                                window.confirm(
                                  `¿Reconectar la voz de "${t.name}"? Se creará un agente de Retell NUEVO (el anterior se descarta) y se asegura su número Twilio. No borra ningún dato. Requiere plan con voz (Professional/Enterprise).`,
                                )
                              ) {
                                provisionVoice.mutate(t.id)
                              }
                            }}
                            disabled={provisionVoice.isPending}
                            className="rounded-md border border-border p-1.5 text-text-secondary transition hover:bg-text-primary/5 disabled:opacity-60"
                          >
                            {provisionVoice.isPending && provisionVoice.variables === t.id ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <PhoneCall className="h-3.5 w-3.5" />
                            )}
                          </button>
                          <button title="Exportar datos" onClick={() => exportTenant(t)} className="rounded-md border border-border p-1.5 text-text-secondary transition hover:bg-text-primary/5">
                            <Download className="h-3.5 w-3.5" />
                          </button>
                          <button
                            title="Eliminar negocio y todos sus datos"
                            onClick={() => {
                              if (window.confirm(`¿Eliminar "${t.name}" y TODOS sus datos? Esta acción es irreversible.`)) {
                                deleteTenant.mutate(t.id)
                              }
                            }}
                            className="rounded-md border border-red-500/30 p-1.5 text-red-400 transition hover:bg-red-500/10"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {visibleTenants.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-text-secondary">
                        {q ? 'Sin resultados para tu búsqueda.' : 'Aún no hay negocios registrados.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
          <p className="mt-3 text-xs text-text-secondary">
            <strong className="text-text-primary">Desactivar</strong> bloquea al instante el panel del dueño y
            detiene su agente de WhatsApp/Instagram y llamadas. <strong className="text-text-primary">Activar</strong>{' '}
            lo reactiva. Los datos nunca se borran salvo que uses "Eliminar".
          </p>
        </section>
      )}

      {/* ───────────────── USO Y CONSUMO ───────────────── */}
      {tab === 'uso' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <Kpi icon={MessageSquare} label="Mensajes totales" value={totals?.total_messages} />
            <Kpi icon={Phone} label="Llamadas totales" value={totals?.total_calls} />
            <Kpi icon={DollarSign} label="Costo Claude total" value={totals ? `$${totals.claude_usd_total}` : undefined} />
            <Kpi icon={TrendingDown} label="Costo real total/mes" value={totals ? soles(totals.real_cost_pen_total) : undefined} />
            <Kpi icon={Wallet} label="Ingreso mensual (MRR)" value={totals ? soles(totals.mrr_pen) : undefined} accent />
          </div>

          <section className="card-base">
            <h3 className="mb-1 font-heading font-semibold text-text-primary">Consumo e ingreso por negocio</h3>
            <p className="mb-4 text-xs text-text-secondary">
              Consumo <strong className="text-text-primary">REAL</strong> por negocio (nada estimado): mensajes y
              llamadas reales, tokens y costo de Claude medidos de verdad, y el <strong className="text-text-primary">costo
              real</strong> = Claude + voz (segundos de llamada) + WhatsApp (conversaciones). Pasa el cursor sobre el
              costo para ver el desglose. Ordenado por costo de Claude (mayor primero).
            </p>
            {analytics.isLoading ? (
              <div className="flex justify-center py-10">
                <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="text-xs uppercase text-text-secondary">
                    <tr className="border-b border-border">
                      <th className="py-2 pr-3">Negocio</th>
                      <th className="py-2 pr-3">Plan</th>
                      <th className="py-2 pr-3 text-right">Contactos</th>
                      <th className="py-2 pr-3 text-right">Mensajes</th>
                      <th className="py-2 pr-3 text-right">Llamadas</th>
                      <th className="py-2 pr-3 text-right">Tokens</th>
                      <th className="py-2 pr-3 text-right">Claude $</th>
                      <th className="py-2 pr-3 text-right">Costo real</th>
                      <th className="py-2 pr-3 text-right">Ingreso</th>
                      <th className="py-2 pr-3 text-right">Ganancia</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...(analytics.data?.tenants ?? [])]
                      .sort((a, b) => b.claude_usd - a.claude_usd)
                      .map((s) => (
                        <tr key={s.id} className="border-b border-border/50">
                          <td className="py-2.5 pr-3">
                            <span className="font-medium text-text-primary">{s.name}</span>
                            {!s.is_active && <span className="ml-2 rounded bg-red-500/10 px-1.5 py-0.5 text-xs text-red-400">inactivo</span>}
                          </td>
                          <td className="py-2.5 pr-3 capitalize text-text-secondary">{s.plan}</td>
                          <td className="py-2.5 pr-3 text-right text-text-secondary">{s.contacts}</td>
                          <td className="py-2.5 pr-3 text-right text-text-secondary">{s.messages}</td>
                          <td className="py-2.5 pr-3 text-right text-text-secondary">{s.calls}</td>
                          <td className="py-2.5 pr-3 text-right text-text-secondary">{s.tokens_used.toLocaleString('es-PE')}</td>
                          <td className="py-2.5 pr-3 text-right font-medium text-amber-400">${s.claude_usd}</td>
                          <td className="py-2.5 pr-3 text-right text-red-400" title={`Claude $${s.claude_usd} + Voz $${s.voice_usd} + WhatsApp $${s.whatsapp_usd}`}>
                            {s.cost_pen > 0 ? `−${soles(s.cost_pen)}` : soles(0)}
                          </td>
                          <td className="py-2.5 pr-3 text-right text-text-secondary">
                            {s.plan === 'trial' ? <span title="En prueba (aún no paga)">{soles(s.revenue_pen)}</span> : soles(s.revenue_pen)}
                          </td>
                          <td className={`py-2.5 pr-3 text-right font-medium ${s.profit_pen >= 0 ? 'text-primary' : 'text-red-400'}`}>
                            {soles(s.profit_pen)}
                          </td>
                        </tr>
                      ))}
                    {(analytics.data?.tenants?.length ?? 0) === 0 && (
                      <tr>
                        <td colSpan={10} className="py-8 text-center text-text-secondary">Aún no hay datos de uso.</td>
                      </tr>
                    )}
                  </tbody>
                  {(analytics.data?.tenants?.length ?? 0) > 0 && (
                    <tfoot>
                      <tr className="border-t border-border font-semibold text-text-primary">
                        <td className="py-2.5 pr-3" colSpan={3}>Totales</td>
                        <td className="py-2.5 pr-3 text-right">{totals?.total_messages ?? 0}</td>
                        <td className="py-2.5 pr-3 text-right">{totals?.total_calls ?? 0}</td>
                        <td className="py-2.5 pr-3 text-right">
                          {(analytics.data?.tenants ?? []).reduce((s, t) => s + t.tokens_used, 0).toLocaleString('es-PE')}
                        </td>
                        <td className="py-2.5 pr-3 text-right text-amber-400">${totals?.claude_usd_total ?? 0}</td>
                        <td className="py-2.5 pr-3 text-right text-red-400">
                          {totals && totals.real_cost_pen_total > 0 ? `−${soles(totals.real_cost_pen_total)}` : soles(0)}
                        </td>
                        <td className="py-2.5 pr-3 text-right">{totals ? soles(totals.mrr_pen) : '—'}</td>
                        <td className="py-2.5 pr-3 text-right text-primary">{totals ? soles(totals.est_monthly_profit_pen) : '—'}</td>
                      </tr>
                    </tfoot>
                  )}
                </table>
              </div>
            )}
            <p className="mt-3 text-xs text-text-secondary">
              Ingreso = lo que paga por su plan (los negocios en prueba pagan S/0 hasta que cobres). Costo real =
              Claude (tokens) + voz (minutos) + WhatsApp (conversaciones), convertido a soles. Ganancia = ingreso −
              costo real. Hoy el costo sale en 0 hasta que haya tráfico real (mensajes/llamadas de verdad); apenas
              conectes las APIs y se use, se llena con números reales que puedes comprobar. Las tarifas por unidad
              se ajustan en el backend para que cuadren con tus facturas.
            </p>
          </section>
        </div>
      )}

      {/* ───────────────── COBROS ───────────────── */}
      {tab === 'cobros' && (
        <section className="card-base">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <CalendarClock className="h-5 w-5 text-warning" />
            <h3 className="font-heading font-semibold text-text-primary">Cobros por revisar</h3>
            <span className="rounded-full bg-warning/15 px-2 py-0.5 text-xs font-medium text-warning">
              {billingCount} por revisar
            </span>
          </div>
          <p className="mb-3 text-xs text-text-secondary">
            El negocio te paga por adelantado (Yape/transferencia). Cuando confirmes el pago, marca{' '}
            <strong className="text-text-primary">"Marcar pagado"</strong> (mueve el vencimiento un mes y
            reactiva). Si no pagó, marca <strong className="text-text-primary">"Suspender"</strong> y su
            plataforma se bloquea hasta que pague.
          </p>
          {billing.isLoading ? (
            <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin text-text-secondary" /></div>
          ) : billingCount === 0 ? (
            <p className="py-8 text-center text-sm text-text-secondary">No hay cobros pendientes ni vencimientos próximos. 🎉</p>
          ) : (
            <div className="space-y-2">
              {billing.data!.map((b) => {
                const label =
                  b.payment_state === 'overdue'
                    ? `Vencido hace ${b.days_overdue} día${b.days_overdue === 1 ? '' : 's'}`
                    : b.payment_state === 'suspended'
                      ? 'Suspendido'
                      : `Vence en ${Math.abs(b.days_overdue)} día${Math.abs(b.days_overdue) === 1 ? '' : 's'}`
                const tone =
                  b.payment_state === 'due_soon'
                    ? 'bg-primary/10 text-primary'
                    : 'bg-red-500/10 text-red-400'
                return (
                  <div
                    key={b.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-background/50 px-4 py-3"
                  >
                    <div className="min-w-0">
                      <div className="font-medium text-text-primary">{b.name}</div>
                      <div className="flex flex-wrap items-center gap-2 text-xs text-text-secondary">
                        <span className="capitalize">{b.plan}</span>
                        <span>·</span>
                        <span>{soles(b.amount_pen)}/mes</span>
                        {b.due_at && (
                          <>
                            <span>·</span>
                            <span>vence {new Date(b.due_at).toLocaleDateString('es-PE')}</span>
                          </>
                        )}
                        <span className={`rounded-full px-2 py-0.5 font-medium ${tone}`}>{label}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => confirmPayment.mutate(b.id)}
                        disabled={confirmPayment.isPending}
                        className="flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary/90 disabled:opacity-60"
                      >
                        <BadgeCheck className="h-3.5 w-3.5" />
                        {b.payment_state === 'suspended' ? 'Reactivar (pagó)' : 'Marcar pagado'}
                      </button>
                      {b.payment_state !== 'suspended' && (
                        <button
                          onClick={() => {
                            if (window.confirm(`¿Suspender "${b.name}" por falta de pago? Su panel quedará bloqueado.`)) {
                              suspendBilling.mutate(b.id)
                            }
                          }}
                          disabled={suspendBilling.isPending}
                          className="flex items-center gap-1.5 rounded-lg border border-red-500/30 px-3 py-1.5 text-xs font-semibold text-red-400 transition hover:bg-red-500/10 disabled:opacity-60"
                        >
                          <Ban className="h-3.5 w-3.5" />
                          Suspender
                        </button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      )}

      {/* ───────────────── RECUPERACIÓN ───────────────── */}
      {tab === 'recuperacion' && (
        <section className="card-base">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <KeyRound className="h-5 w-5 text-warning" />
            <h3 className="font-heading font-semibold text-text-primary">Solicitudes de recuperación de contraseña</h3>
            <span className="rounded-full bg-warning/15 px-2 py-0.5 text-xs font-medium text-warning">
              {resetCount} pendiente(s)
            </span>
          </div>
          <p className="mb-3 text-xs text-text-secondary">
            Un dueño pidió recuperar su acceso. <strong className="text-text-primary">Verifica que sea él</strong> (por
            teléfono/correo) antes de restablecer. Al restablecer se genera una contraseña nueva al azar que deberás
            entregarle; él podrá cambiarla luego desde su panel.
          </p>
          {resetRequests.isLoading ? (
            <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin text-text-secondary" /></div>
          ) : resetCount === 0 ? (
            <p className="py-8 text-center text-sm text-text-secondary">No hay solicitudes pendientes.</p>
          ) : (
            <div className="space-y-2">
              {resetRequests.data!.map((r) => (
                <div
                  key={r.id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-background/50 px-4 py-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium text-text-primary">{r.full_name ?? r.email}</div>
                    <div className="text-xs text-text-secondary">
                      {r.email}
                      {r.tenant_name ? ` · ${r.tenant_name}` : ''} ·{' '}
                      {new Date(r.created_at).toLocaleString('es-PE')}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => approveReset.mutate(r.id)}
                      disabled={approveReset.isPending}
                      className="flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary/90 disabled:opacity-60"
                    >
                      {approveReset.isPending ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <KeyRound className="h-3.5 w-3.5" />
                      )}
                      Restablecer contraseña
                    </button>
                    <button
                      onClick={() => dismissReset.mutate(r.id)}
                      disabled={dismissReset.isPending}
                      className="rounded-lg border border-border px-3 py-1.5 text-xs font-semibold text-text-secondary transition hover:bg-text-primary/5 disabled:opacity-60"
                    >
                      Descartar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {logsTenant && <WebhookLogsModal tenant={logsTenant} onClose={() => setLogsTenant(null)} />}
      {resetResult && <PasswordModal result={resetResult} onClose={() => setResetResult(null)} />}
    </div>
  )
}

function PasswordModal({ result, onClose }: { result: ResetResult; onClose: () => void }) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(result.new_password)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      /* clipboard no disponible */
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={onClose}>
      <div
        className="w-full max-w-md overflow-hidden rounded-2xl border border-border bg-card p-6 text-center"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/15 text-primary">
          <KeyRound className="h-7 w-7" />
        </div>
        <h3 className="mb-1 font-heading text-lg font-bold text-text-primary">Contraseña restablecida</h3>
        <p className="mb-4 text-sm text-text-secondary">
          Entrégale esta contraseña a <strong className="text-text-primary">{result.user_email}</strong>. Se
          muestra <strong className="text-text-primary">una sola vez</strong> — cópiala ahora.
        </p>
        <div className="mb-4 flex items-center justify-between gap-2 rounded-xl border border-border bg-background px-4 py-3">
          <code className="select-all font-mono text-lg tracking-wider text-text-primary">
            {result.new_password}
          </code>
          <button
            onClick={copy}
            className="flex flex-shrink-0 items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary/90"
          >
            {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? 'Copiado' : 'Copiar'}
          </button>
        </div>
        <button
          onClick={onClose}
          className="w-full rounded-lg border border-border py-2 text-sm font-semibold text-text-secondary transition hover:bg-text-primary/5"
        >
          Listo
        </button>
      </div>
    </div>
  )
}

function Kpi({
  icon: Icon,
  label,
  value,
  accent = false,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: number | string | undefined
  accent?: boolean
}) {
  return (
    <div className="card-base">
      <div className={`mb-2 flex h-9 w-9 items-center justify-center rounded-lg ${accent ? 'bg-primary/15 text-primary' : 'bg-text-primary/5 text-text-secondary'}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-2xl font-bold text-text-primary">{value ?? '—'}</div>
      <div className="text-xs text-text-secondary">{label}</div>
    </div>
  )
}

function Input({
  label,
  value,
  onChange,
  type = 'text',
  required = false,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  type?: string
  required?: boolean
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-text-secondary">{label}</label>
      <input
        type={type}
        required={required}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm text-text-primary outline-none focus:border-primary"
      />
    </div>
  )
}

interface WebhookLogRow {
  id: string
  source?: string
  event_type?: string
  status?: string
  error_message?: string | null
  created_at?: string
}

function WebhookLogsModal({ tenant, onClose }: { tenant: Tenant; onClose: () => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-webhooks', tenant.id],
    queryFn: async () => (await api.get<WebhookLogRow[]>(`/admin/tenants/${tenant.id}/webhooks`)).data,
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={onClose}>
      <div className="max-h-[80vh] w-full max-w-3xl overflow-hidden rounded-2xl border border-border bg-card" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <h3 className="font-heading font-semibold text-text-primary">Logs de webhooks · {tenant.name}</h3>
          <button onClick={onClose} className="text-text-secondary hover:text-text-primary">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="max-h-[65vh] overflow-auto p-4 scrollbar-thin">
          {isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
            </div>
          ) : !data || data.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-secondary">Sin eventos de webhook todavía.</p>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="uppercase text-text-secondary">
                <tr className="border-b border-border">
                  <th className="py-2 pr-3">Fecha</th>
                  <th className="py-2 pr-3">Fuente</th>
                  <th className="py-2 pr-3">Evento</th>
                  <th className="py-2 pr-3">Estado</th>
                </tr>
              </thead>
              <tbody>
                {data.map((log) => (
                  <tr key={log.id} className="border-b border-border/50 align-top">
                    <td className="py-2 pr-3 text-text-secondary">{log.created_at ? new Date(log.created_at).toLocaleString('es-PE') : '—'}</td>
                    <td className="py-2 pr-3 text-text-primary">{log.source ?? '—'}</td>
                    <td className="py-2 pr-3 text-text-primary">{log.event_type ?? '—'}</td>
                    <td className="py-2 pr-3">
                      <span className={log.status === 'failed' || log.error_message ? 'text-red-400' : 'text-primary'}>{log.status ?? '—'}</span>
                      {log.error_message && <div className="text-red-400/80">{log.error_message}</div>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
