import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import {
  MessageSquare,
  Settings,
  PartyPopper,
  ChevronRight,
  Check,
  Loader2,
  CheckCircle2,
} from 'lucide-react'
import { api, apiErrorMessage } from '../../lib/api'
import { cn } from '../../lib/utils'
import { toast } from '../../stores/ui.store'
import { Logo } from '../../components/ui/Logo'

const STEPS = [
  { label: 'Bienvenida', hint: 'Conoce la plataforma' },
  { label: 'WhatsApp', hint: 'Conecta tu número de WhatsApp Business' },
  { label: 'Agente IA', hint: 'Configura cómo responde tu agente' },
  { label: 'Listo', hint: '¡A funcionar!' },
]

/** Stepper con números, checks de completado y tooltip por paso. */
function Stepper({ step }: { step: number }) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {STEPS.map((s, i) => {
          const done = i < step
          const active = i === step
          return (
            <div key={s.label} className="flex flex-1 items-center last:flex-none">
              <div className="group relative flex flex-col items-center">
                <motion.div
                  initial={false}
                  animate={{ scale: active ? 1.1 : 1 }}
                  className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-full border text-xs font-semibold transition-colors',
                    done && 'border-primary bg-primary text-white',
                    active && 'border-primary bg-primary/15 text-primary',
                    !done && !active && 'border-border bg-card text-text-secondary',
                  )}
                >
                  {done ? <Check className="h-4 w-4" /> : i + 1}
                </motion.div>
                <span
                  className={cn(
                    'mt-1.5 hidden text-[11px] sm:block',
                    active || done ? 'text-text-primary' : 'text-text-secondary',
                  )}
                >
                  {s.label}
                </span>
                {/* Tooltip */}
                <div className="pointer-events-none absolute bottom-full mb-2 whitespace-nowrap rounded-md border border-border bg-card px-2 py-1 text-[11px] text-text-secondary opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
                  {s.hint}
                </div>
              </div>
              {i < STEPS.length - 1 && (
                <div className="mx-2 h-0.5 flex-1 overflow-hidden rounded-full bg-border">
                  <motion.div
                    initial={false}
                    animate={{ width: done ? '100%' : '0%' }}
                    transition={{ duration: 0.4 }}
                    className="h-full bg-primary"
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

interface WhatsAppStatus {
  connected: boolean
  phone_number_id: string | null
  webhook_url: string
  verify_token: string | null
  verified: boolean | null
}

export function OnboardingPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const isLast = step === 3

  function finish() {
    navigate('/app')
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-lg"
      >
        <Stepper step={step} />

        <div className="card-base p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -24 }}
              transition={{ duration: 0.25 }}
            >
              {step === 0 && (
                <StepShell
                  iconNode={<Logo size={64} />}
                  title="¡Bienvenido a AgentePro! 🚀"
                  body="Tu plataforma de automatización con IA está lista. En unos pasos tendrás tu agente atendiendo 24/7."
                />
              )}

              {step === 1 && <WhatsAppStep />}

              {step === 2 && (
                <StepShell
                  icon={Settings}
                  title="Configura tu agente IA"
                  body='Define el nombre, horario, servicios y preguntas frecuentes desde la sección "Agente IA". Puedes probarlo en vivo antes de activarlo.'
                />
              )}

              {step === 3 && (
                <StepShell
                  icon={PartyPopper}
                  title="¡Todo listo!"
                  body="Tu agente ya puede responder. Revisa el dashboard para ver conversaciones, llamadas y métricas en tiempo real."
                />
              )}
            </motion.div>
          </AnimatePresence>

          <div className="mt-8 flex items-center justify-between">
            <button
              onClick={finish}
              className="text-sm text-text-secondary hover:text-text-primary"
            >
              Saltar
            </button>
            {isLast ? (
              <button onClick={finish} className="btn-primary">
                <Check className="h-4 w-4" /> Ir al dashboard
              </button>
            ) : (
              <button onClick={() => setStep((s) => s + 1)} className="btn-primary">
                Siguiente <ChevronRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function StepShell({
  icon: Icon,
  iconNode,
  title,
  body,
}: {
  icon?: React.ComponentType<{ className?: string }>
  iconNode?: React.ReactNode
  title: string
  body: string
}) {
  return (
    <div className="text-center">
      {iconNode ? (
        <div className="mx-auto mb-5 flex w-fit items-center justify-center">{iconNode}</div>
      ) : (
        Icon && (
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 text-primary">
            <Icon className="h-8 w-8" />
          </div>
        )
      )}
      <h1 className="mb-3 font-heading text-2xl font-bold text-text-primary">{title}</h1>
      <p className="text-sm leading-relaxed text-text-secondary">{body}</p>
    </div>
  )
}

function WhatsAppStep() {
  const [form, setForm] = useState({ phone_number_id: '', waba_id: '', access_token: '' })
  const [status, setStatus] = useState<WhatsAppStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  function update(field: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function connect(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const body = {
        phone_number_id: form.phone_number_id,
        access_token: form.access_token,
        ...(form.waba_id ? { waba_id: form.waba_id } : {}),
      }
      const res = await api.post<WhatsAppStatus>('/whatsapp/connect', body)
      setStatus(res.data)
      toast({ variant: 'success', title: 'WhatsApp conectado', description: 'Ya puedes recibir mensajes.' })
    } catch (err) {
      setError(apiErrorMessage(err, 'No se pudo conectar WhatsApp'))
    } finally {
      setLoading(false)
    }
  }

  if (status?.connected) {
    return (
      <div className="text-center">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 text-primary">
          <CheckCircle2 className="h-8 w-8" />
        </div>
        <h1 className="mb-2 font-heading text-2xl font-bold text-text-primary">WhatsApp conectado</h1>
        <p className="mb-4 text-sm text-text-secondary">
          Configura este webhook en la app de Meta para recibir mensajes:
        </p>
        <div className="space-y-2 text-left">
          <Labeled label="Webhook URL">{status.webhook_url}</Labeled>
          {status.verify_token && (
            <Labeled label="Verify token">{status.verify_token}</Labeled>
          )}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-5 text-center">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 text-primary">
          <MessageSquare className="h-8 w-8" />
        </div>
        <h1 className="mb-2 font-heading text-2xl font-bold text-text-primary">
          Conecta WhatsApp Business
        </h1>
        <p className="text-sm leading-relaxed text-text-secondary">
          En developers.facebook.com crea una app, agrega el producto WhatsApp y copia tu Phone
          Number ID y Access Token.
        </p>
      </div>

      <form onSubmit={connect} className="space-y-3 text-left">
        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
            {error}
          </div>
        )}
        <Field label="Phone Number ID">
          <input
            required
            value={form.phone_number_id}
            onChange={(e) => update('phone_number_id', e.target.value)}
            className="input-base"
          />
        </Field>
        <Field label="WABA ID (opcional)">
          <input
            value={form.waba_id}
            onChange={(e) => update('waba_id', e.target.value)}
            className="input-base"
          />
        </Field>
        <Field label="Access Token">
          <input
            required
            value={form.access_token}
            onChange={(e) => update('access_token', e.target.value)}
            className="input-base"
          />
        </Field>
        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary/90 disabled:opacity-60"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          Conectar WhatsApp
        </button>
        <p className="text-center text-xs text-text-secondary">
          Puedes hacerlo más tarde desde Configuración.
        </p>
      </form>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-text-secondary">{label}</label>
      {children}
    </div>
  )
}

function Labeled({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1 text-xs font-medium text-text-secondary">{label}</div>
      <code className="block break-all rounded-lg bg-background p-2 text-xs text-text-primary">
        {children}
      </code>
    </div>
  )
}
