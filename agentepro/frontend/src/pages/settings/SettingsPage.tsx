import { useQuery } from '@tanstack/react-query'
import { Loader2, Building2, Phone, Webhook, CreditCard } from 'lucide-react'
import { api } from '../../lib/api'
import { useAuthStore } from '../../stores/auth.store'
import { AppearanceSettings } from '../../components/settings/AppearanceSettings'
import { NotionSettings } from '../../components/settings/NotionSettings'

interface Tenant {
  id: string
  name: string
  slug: string
  business_type: string
  plan: string
  twilio_phone_number: string | null
  messages_used_this_month: number
  calls_used_this_month: number
  is_provisioned: boolean
}

export function SettingsPage() {
  const user = useAuthStore((s) => s.user)
  const { data: tenant, isLoading, isError } = useQuery({
    queryKey: ['tenant-me'],
    queryFn: async () => (await api.get<Tenant>('/tenants/me')).data,
    retry: false,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
      </div>
    )
  }

  if (isError || !tenant) {
    return (
      <div className="mx-auto max-w-md rounded-xl border border-border bg-card p-6 text-center text-sm text-text-secondary">
        No se pudo cargar la configuración del negocio. Si tu cuenta es de
        administrador de la plataforma, usa el panel de Super Admin.
      </div>
    )
  }

  const webhookUrl = `${window.location.origin.replace(':5173', ':8000')}/webhooks/whatsapp/${tenant.slug}`

  return (
    <div className="max-w-2xl space-y-5">
      <section className="card-base space-y-3">
        <div className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-text-primary">Negocio</h3>
        </div>
        <Row label="Nombre" value={tenant.name} />
        <Row label="Tipo" value={tenant.business_type} />
        <Row label="Plan" value={tenant.plan.toUpperCase()} />
        <Row label="Propietario" value={user?.full_name ?? '—'} />
        <Row label="Email" value={user?.email ?? '—'} />
      </section>

      <section className="card-base space-y-3">
        <div className="flex items-center gap-2">
          <CreditCard className="h-5 w-5 text-secondary" />
          <h3 className="font-heading font-semibold text-text-primary">Uso del mes</h3>
        </div>
        <Row label="Mensajes usados" value={String(tenant.messages_used_this_month)} />
        <Row label="Llamadas usadas" value={String(tenant.calls_used_this_month)} />
      </section>

      <section className="card-base space-y-3">
        <div className="flex items-center gap-2">
          <Phone className="h-5 w-5 text-warning" />
          <h3 className="font-heading font-semibold text-text-primary">Telefonía y canales</h3>
        </div>
        <Row label="Número Twilio" value={tenant.twilio_phone_number ?? 'No asignado'} />
        <div>
          <div className="mb-1 flex items-center gap-2 text-sm font-medium text-text-secondary">
            <Webhook className="h-4 w-4" /> Webhook de WhatsApp (Meta)
          </div>
          <code className="block break-all rounded-lg bg-background p-2 text-xs text-text-primary">
            {webhookUrl}
          </code>
        </div>
      </section>

      <NotionSettings />

      <AppearanceSettings />
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border/50 pb-2 text-sm">
      <span className="text-text-secondary">{label}</span>
      <span className="font-medium text-text-primary">{value}</span>
    </div>
  )
}
