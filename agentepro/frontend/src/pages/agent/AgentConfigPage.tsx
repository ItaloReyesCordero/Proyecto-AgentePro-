import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bot, Loader2, Plus, Trash2, Save, Send } from 'lucide-react'
import { api } from '../../lib/api'
import { useUIStore } from '../../stores/ui.store'

interface Faq {
  question: string
  answer: string
  category?: string
}
interface Service {
  name: string
  description?: string
  price?: number
}
interface AgentConfig {
  agent_name: string
  welcome_message: string
  outside_hours_message: string
  escalation_phone: string | null
  escalation_email: string | null
  owner_contacts: string[]
  owner_handoff_message: string
  faqs: Faq[]
  services: Service[]
}

interface TestResult {
  reply: string
  intent: string
  confidence: number
  lead_score: number
  lead_stage: string
  should_escalate: boolean
}

export function AgentConfigPage() {
  const queryClient = useQueryClient()
  const addToast = useUIStore((s) => s.addToast)
  const { data, isLoading } = useQuery({
    queryKey: ['agent-config'],
    queryFn: async () => (await api.get<AgentConfig>('/agent/config')).data,
  })
  const [config, setConfig] = useState<AgentConfig | null>(null)

  useEffect(() => {
    if (data) setConfig(data)
  }, [data])

  const save = useMutation({
    mutationFn: async (payload: AgentConfig) => (await api.put('/agent/config', payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-config'] })
      addToast({ title: 'Configuración guardada', variant: 'success' })
    },
  })

  if (isLoading || !config) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
      </div>
    )
  }

  function update<K extends keyof AgentConfig>(key: K, value: AgentConfig[K]) {
    setConfig((c) => (c ? { ...c, [key]: value } : c))
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div className="space-y-5 lg:col-span-2">
        <section className="card-base space-y-4">
          <h3 className="font-heading font-semibold text-text-primary">Identidad del agente</h3>
          <Field label="Nombre del agente">
            <input
              className="input-base"
              value={config.agent_name}
              onChange={(e) => update('agent_name', e.target.value)}
            />
          </Field>
          <Field label="Mensaje de bienvenida">
            <textarea
              className="input-base min-h-20"
              value={config.welcome_message}
              onChange={(e) => update('welcome_message', e.target.value)}
            />
          </Field>
          <Field label="Mensaje fuera de horario">
            <textarea
              className="input-base min-h-16"
              value={config.outside_hours_message}
              onChange={(e) => update('outside_hours_message', e.target.value)}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Teléfono de escalación">
              <input
                className="input-base"
                value={config.escalation_phone ?? ''}
                onChange={(e) => update('escalation_phone', e.target.value)}
              />
            </Field>
            <Field label="Email de escalación">
              <input
                className="input-base"
                value={config.escalation_email ?? ''}
                onChange={(e) => update('escalation_email', e.target.value)}
              />
            </Field>
          </div>
        </section>

        <section className="card-base space-y-4">
          <div>
            <h3 className="font-heading font-semibold text-text-primary">Pasar con el dueño</h3>
            <p className="text-sm text-text-secondary">
              Números de amigos/familiares del dueño. Si uno de ellos escribe, el bot NO responde:
              manda un aviso y te avisa para que lo atiendas tú personalmente.
            </p>
          </div>
          <Field label="Números conocidos (uno por línea)">
            <textarea
              className="input-base min-h-20"
              placeholder={'+51999888777\n999000111'}
              value={config.owner_contacts.join('\n')}
              onChange={(e) =>
                update(
                  'owner_contacts',
                  e.target.value
                    .split(/[\n,]/)
                    .map((s) => s.trim())
                    .filter(Boolean),
                )
              }
            />
          </Field>
          <Field label="Mensaje al pasar con el dueño">
            <textarea
              className="input-base min-h-16"
              value={config.owner_handoff_message}
              onChange={(e) => update('owner_handoff_message', e.target.value)}
            />
          </Field>
        </section>

        <section className="card-base space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-heading font-semibold text-text-primary">Preguntas frecuentes</h3>
            <button
              onClick={() => update('faqs', [...config.faqs, { question: '', answer: '' }])}
              className="flex items-center gap-1 text-sm text-primary hover:underline"
            >
              <Plus className="h-4 w-4" /> Agregar
            </button>
          </div>
          {config.faqs.map((faq, i) => (
            <div key={i} className="space-y-2 rounded-lg border border-border p-3">
              <input
                className="input-base"
                placeholder="Pregunta"
                value={faq.question}
                onChange={(e) => {
                  const faqs = [...config.faqs]
                  faqs[i] = { ...faq, question: e.target.value }
                  update('faqs', faqs)
                }}
              />
              <div className="flex gap-2">
                <textarea
                  className="input-base flex-1"
                  placeholder="Respuesta"
                  value={faq.answer}
                  onChange={(e) => {
                    const faqs = [...config.faqs]
                    faqs[i] = { ...faq, answer: e.target.value }
                    update('faqs', faqs)
                  }}
                />
                <button
                  onClick={() => update('faqs', config.faqs.filter((_, idx) => idx !== i))}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </section>

        <button onClick={() => save.mutate(config)} disabled={save.isPending} className="btn-primary">
          {save.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          Guardar configuración
        </button>
      </div>

      <TestPanel />
    </div>
  )
}

function TestPanel() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<TestResult | null>(null)
  const test = useMutation({
    mutationFn: async (msg: string) =>
      (await api.post<TestResult>('/agent/config/test', { message: msg })).data,
    onSuccess: (data) => setResult(data),
  })

  return (
    <div className="card-base flex h-fit flex-col gap-3">
      <div className="flex items-center gap-2">
        <Bot className="h-5 w-5 text-primary" />
        <h3 className="font-heading font-semibold text-text-primary">Probar agente</h3>
      </div>
      <div className="flex gap-2">
        <input
          className="input-base flex-1"
          placeholder="Escribe un mensaje de prueba..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && message.trim() && test.mutate(message)}
        />
        <button
          onClick={() => message.trim() && test.mutate(message)}
          disabled={test.isPending}
          className="btn-primary"
        >
          {test.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </div>
      {result && (
        <div className="space-y-2">
          <div className="rounded-lg border border-primary/20 bg-primary/10 p-3 text-sm text-text-primary">
            {result.reply}
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary">
            <Meta label="Intención" value={result.intent} />
            <Meta label="Confianza" value={`${Math.round(result.confidence * 100)}%`} />
            <Meta label="Lead score" value={String(result.lead_score)} />
            <Meta label="Etapa" value={result.lead_stage} />
          </div>
          {result.should_escalate && (
            <p className="text-xs text-warning">⚠️ Este mensaje activaría un escalado a humano.</p>
          )}
        </div>
      )}
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

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-background px-2 py-1.5">
      <span className="text-text-secondary">{label}: </span>
      <span className="font-medium text-text-primary">{value}</span>
    </div>
  )
}
