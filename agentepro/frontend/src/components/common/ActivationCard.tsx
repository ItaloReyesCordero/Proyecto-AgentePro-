import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { CheckCircle2, Circle, MessageSquare, Bot, Send, ArrowRight } from 'lucide-react'
import { api } from '../../lib/api'

interface WhatsAppStatus {
  connected: boolean
  phone_number_id: string | null
}
interface AgentConfig {
  faqs?: { question: string; answer: string }[]
  welcome_message?: string
}

/**
 * Tarjeta de activación: muestra el estado de WhatsApp y una checklist para
 * que el dueño deje su agente listo. Desaparece cuando WhatsApp está conectado
 * y el agente tiene FAQs configuradas.
 */
export function ActivationCard() {
  const wa = useQuery({
    queryKey: ['whatsapp-status'],
    queryFn: async () => (await api.get<WhatsAppStatus>('/whatsapp/status')).data,
  })
  const agent = useQuery({
    queryKey: ['agent-config'],
    queryFn: async () => (await api.get<AgentConfig>('/agent/config')).data,
  })

  // Mientras carga, no mostramos nada (evita parpadeo).
  if (wa.isLoading || agent.isLoading) return null

  const waConnected = !!wa.data?.connected
  const agentReady = (agent.data?.faqs?.length ?? 0) > 0

  // Si ya está todo listo, no estorbamos.
  if (waConnected && agentReady) return null

  return (
    <section className="card-base border-primary/30">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-heading font-semibold text-text-primary">🚀 Termina de activar tu agente</h3>
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            waConnected
              ? 'bg-primary/10 text-primary'
              : 'bg-warning/15 text-warning'
          }`}
        >
          WhatsApp {waConnected ? 'conectado' : 'desconectado'}
        </span>
      </div>

      <div className="space-y-2">
        <Step
          done={waConnected}
          icon={MessageSquare}
          title="Conecta WhatsApp"
          desc="Vincula tu número de WhatsApp Business para recibir mensajes."
          actionLabel="Conectar"
          to="/onboarding"
        />
        <Step
          done={agentReady}
          icon={Bot}
          title="Configura tu agente"
          desc="Define su nombre, mensaje de bienvenida y preguntas frecuentes."
          actionLabel="Configurar"
          to="/app/agent"
        />
        <Step
          done={false}
          icon={Send}
          title="Pruébalo"
          desc="Escríbele un mensaje de prueba y mira cómo responde."
          actionLabel="Probar"
          to="/app/agent"
          alwaysAction
        />
      </div>
    </section>
  )
}

function Step({
  done,
  icon: Icon,
  title,
  desc,
  actionLabel,
  to,
  alwaysAction = false,
}: {
  done: boolean
  icon: React.ComponentType<{ className?: string }>
  title: string
  desc: string
  actionLabel: string
  to: string
  alwaysAction?: boolean
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-background/50 p-3">
      {done ? (
        <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-primary" />
      ) : (
        <Circle className="h-5 w-5 flex-shrink-0 text-text-secondary" />
      )}
      <div className="flex items-center gap-2 text-text-secondary">
        <Icon className="h-4 w-4 flex-shrink-0" />
      </div>
      <div className="min-w-0 flex-1">
        <p className={`text-sm font-medium ${done ? 'text-text-secondary line-through' : 'text-text-primary'}`}>
          {title}
        </p>
        <p className="truncate text-xs text-text-secondary">{desc}</p>
      </div>
      {(!done || alwaysAction) && (
        <Link
          to={to}
          className="flex flex-shrink-0 items-center gap-1 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primary/90"
        >
          {actionLabel} <ArrowRight className="h-3 w-3" />
        </Link>
      )}
    </div>
  )
}
