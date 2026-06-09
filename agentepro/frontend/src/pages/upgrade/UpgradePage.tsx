import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Lock, LogOut, MessageCircle, Smartphone, Building2, User as UserIcon } from 'lucide-react'
import { useAuthStore } from '../../stores/auth.store'
import { api } from '../../lib/api'

interface PaymentInfo {
  yape_number: string
  account_holder: string
  bank_account: string
  contact_whatsapp: string
  note: string
  configured: boolean
}

/**
 * Pantalla que ve el cliente cuando su prueba terminó O fue suspendido por falta
 * de pago. El backend bloquea (402 TRIAL_EXPIRED / PAYMENT_OVERDUE) todos los
 * endpoints del negocio, así que esta página solo llama al endpoint PÚBLICO
 * /tenants/payment-info (nunca a endpoints del negocio) para evitar bucles.
 */
export function UpgradePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const { data: pay } = useQuery({
    queryKey: ['payment-info'],
    queryFn: async () => (await api.get<PaymentInfo>('/tenants/payment-info')).data,
  })

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const waNumber = pay?.contact_whatsapp || '51999999999'

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md text-center">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-warning/15 text-warning">
          <Lock className="h-8 w-8" />
        </div>
        <h1 className="mb-3 font-heading text-2xl font-bold text-text-primary">
          Tu servicio está en pausa
        </h1>
        <p className="mb-6 text-sm leading-relaxed text-text-secondary">
          {user?.full_name ? `${user.full_name}, tu` : 'Tu'} acceso quedó bloqueado porque tu prueba
          terminó o tu mensualidad está pendiente. Tu agente dejó de responder, pero{' '}
          <strong className="text-text-primary">tus datos siguen guardados</strong>. Paga tu
          mensualidad por adelantado para reactivar todo al instante.
        </p>

        <div className="rounded-2xl border border-border bg-card p-6 text-left">
          {pay?.configured ? (
            <>
              <p className="mb-4 text-sm font-medium text-text-primary">
                Paga por adelantado a estos datos:
              </p>
              <div className="space-y-3 text-sm">
                {pay.yape_number && (
                  <div className="flex items-center gap-3">
                    <Smartphone className="h-4 w-4 flex-shrink-0 text-primary" />
                    <span className="text-text-secondary">Yape / Plin:</span>
                    <span className="font-semibold text-text-primary">{pay.yape_number}</span>
                  </div>
                )}
                {pay.account_holder && (
                  <div className="flex items-center gap-3">
                    <UserIcon className="h-4 w-4 flex-shrink-0 text-primary" />
                    <span className="text-text-secondary">Titular:</span>
                    <span className="font-semibold text-text-primary">{pay.account_holder}</span>
                  </div>
                )}
                {pay.bank_account && (
                  <div className="flex items-center gap-3">
                    <Building2 className="h-4 w-4 flex-shrink-0 text-primary" />
                    <span className="text-text-secondary">Cuenta:</span>
                    <span className="font-semibold text-text-primary">{pay.bank_account}</span>
                  </div>
                )}
              </div>
              {pay.note && <p className="mt-4 text-xs text-text-secondary">{pay.note}</p>}
              <p className="mt-4 text-xs text-text-secondary">
                Tras pagar, envíanos tu comprobante por WhatsApp y reactivamos tu cuenta.
              </p>
            </>
          ) : (
            <p className="mb-4 text-sm text-text-secondary">
              Escríbenos para activar tu plan y seguir atendiendo a tus clientes 24/7:
            </p>
          )}

          <a
            href={`https://wa.me/${waNumber.replaceAll(/[^0-9]/g, '')}`}
            target="_blank"
            rel="noreferrer"
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary/90"
          >
            <MessageCircle className="h-4 w-4" /> Enviar comprobante / Reactivar
          </a>
          <button
            onClick={handleLogout}
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-border py-2.5 text-sm font-semibold text-text-secondary transition hover:bg-text-primary/5"
          >
            <LogOut className="h-4 w-4" /> Cerrar sesión
          </button>
        </div>

        <p className="mt-4 text-xs text-text-secondary">
          Tus datos siguen guardados. Al confirmar tu pago, todo vuelve a estar disponible.
        </p>
      </div>
    </div>
  )
}
