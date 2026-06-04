import { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { Loader2, ArrowLeft } from 'lucide-react'
import { api, apiErrorMessage } from '../../lib/api'
import { useAuthStore, type User } from '../../stores/auth.store'
import { PasswordInput } from '../../components/ui/PasswordInput'
import { Logo } from '../../components/ui/Logo'

interface TokenResponse {
  access_token: string
  refresh_token: string
  user: User
}

const BUSINESS_TYPES = [
  { value: 'healthcare', label: 'Clínica / Salud' },
  { value: 'education', label: 'Academia / Educación' },
  { value: 'retail', label: 'Tienda / Retail' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'real_estate', label: 'Inmobiliaria' },
  { value: 'services', label: 'Servicios' },
  { value: 'other', label: 'Otro' },
]

const PLAN_LABELS: Record<string, string> = {
  inicial: 'Inicial — S/ 149/mes',
  basic: 'Basic — S/ 249/mes',
  professional: 'Professional — S/ 449/mes',
  enterprise: 'Enterprise — S/ 799/mes',
}

export function RegisterPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const plan = (searchParams.get('plan') ?? '').toLowerCase()
  const planLabel = PLAN_LABELS[plan]
  const setAuth = useAuthStore((s) => s.setAuth)
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    business_name: '',
    business_type: 'services',
  })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  function update(field: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await api.post<TokenResponse>('/auth/register', form)
      setAuth(res.data.access_token, res.data.refresh_token, res.data.user)
      navigate(plan ? `/onboarding?plan=${plan}` : '/onboarding')
    } catch (err) {
      setError(apiErrorMessage(err, 'No se pudo registrar'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <Link
          to="/"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-text-secondary transition hover:text-text-primary"
        >
          <ArrowLeft className="h-4 w-4" /> Volver al inicio
        </Link>
        <div className="mb-6 flex flex-col items-center text-center">
          <Logo size={60} className="mb-3" />
          <h1 className="font-heading text-2xl font-bold text-text-primary">Crea tu cuenta</h1>
          <p className="mt-1 text-sm text-text-secondary">Activa tu agente IA en minutos</p>
          {planLabel && (
            <span className="mt-3 inline-block rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              Plan elegido: {planLabel} · 14 días de prueba gratis
            </span>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-2xl border border-border bg-card p-6"
        >
          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
              {error}
            </div>
          )}
          <Field label="Tu nombre">
            <input
              required
              value={form.full_name}
              onChange={(e) => update('full_name', e.target.value)}
              className="input-base"
            />
          </Field>
          <Field label="Nombre del negocio">
            <input
              required
              value={form.business_name}
              onChange={(e) => update('business_name', e.target.value)}
              className="input-base"
            />
          </Field>
          <Field label="Tipo de negocio">
            <select
              value={form.business_type}
              onChange={(e) => update('business_type', e.target.value)}
              className="input-base"
            >
              {BUSINESS_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Email">
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => update('email', e.target.value)}
              className="input-base"
            />
          </Field>
          <Field label="Contraseña">
            <PasswordInput
              required
              minLength={6}
              value={form.password}
              onChange={(e) => update('password', e.target.value)}
            />
          </Field>
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary/90 disabled:opacity-60"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            Crear cuenta
          </button>
          <p className="text-center text-sm text-text-secondary">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="text-primary hover:underline">
              Inicia sesión
            </Link>
          </p>
        </form>
      </div>
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
