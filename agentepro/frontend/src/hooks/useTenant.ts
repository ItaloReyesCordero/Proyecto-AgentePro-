import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

/** Datos del negocio autenticado (/tenants/me). Incluye los módulos del plan. */
export interface TenantMe {
  id: string
  name: string
  plan: string
  is_active: boolean
  is_provisioned: boolean
  messages_used_this_month: number
  calls_used_this_month: number
  trial_ends_at: string | null
  /** Módulos habilitados por el plan: 'contacts'|'instagram'|'appointments'|'voice'|'automations'. */
  features: string[]
  message_limit: number
  call_limit: number
  payment_state: string
  payment_due_at: string | null
}

/** Query compartida del negocio actual (misma queryKey que TrialBanner → se deduplica). */
export function useMyTenant() {
  return useQuery({
    queryKey: ['tenant-me'],
    queryFn: async () => (await api.get<TenantMe>('/tenants/me')).data,
  })
}

/**
 * Devuelve si el negocio tiene un módulo habilitado por su plan.
 * Mientras carga, asume que NO (evita parpadeo mostrando algo que luego se oculta).
 */
export function useHasFeature(feature: string): boolean {
  const { data } = useMyTenant()
  return Boolean(data?.features?.includes(feature))
}
