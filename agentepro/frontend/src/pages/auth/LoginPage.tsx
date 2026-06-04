import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
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

export function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await api.post<TokenResponse>('/auth/login', { email, password })
      setAuth(res.data.access_token, res.data.refresh_token, res.data.user)
      navigate(res.data.user.role === 'superadmin' ? '/app/admin' : '/app')
    } catch (err) {
      setError(apiErrorMessage(err, 'Credenciales inválidas'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <Link
          to="/"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-text-secondary transition hover:text-text-primary"
        >
          <ArrowLeft className="h-4 w-4" /> Volver al inicio
        </Link>
        <div className="mb-8 flex flex-col items-center text-center">
          <Logo size={64} className="mb-3" />
          <h1 className="font-heading text-2xl font-bold text-text-primary">AgentePro</h1>
          <p className="mt-1 text-sm text-text-secondary">Inicia sesión en tu plataforma</p>
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
          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-base"
              placeholder="tu@negocio.pe"
            />
          </div>
          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="block text-sm font-medium text-text-secondary">Contraseña</label>
              <Link to="/forgot-password" className="text-xs text-primary hover:underline">
                ¿Olvidaste tu contraseña?
              </Link>
            </div>
            <PasswordInput
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-sm font-semibold text-white transition hover:bg-primary/90 disabled:opacity-60"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            Ingresar
          </button>
          <p className="text-center text-sm text-text-secondary">
            ¿No tienes cuenta?{' '}
            <Link to="/register" className="text-primary hover:underline">
              Regístrate
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
