import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { KeyRound, Loader2, MailCheck, ArrowLeft } from 'lucide-react'
import { api, apiErrorMessage } from '../../lib/api'

/**
 * Recuperación de contraseña para DUEÑOS de negocio. Envía la solicitud al
 * backend (que no revela si el correo existe) y el super admin la procesa.
 * No aplica a cuentas de super admin.
 */
export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await api.post('/auth/password-reset-request', { email })
      setSent(true)
    } catch (err) {
      setError(apiErrorMessage(err, 'No se pudo enviar la solicitud'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-sm"
      >
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            {sent ? <MailCheck className="h-7 w-7 text-white" /> : <KeyRound className="h-7 w-7 text-white" />}
          </div>
          <h1 className="font-heading text-2xl font-bold text-text-primary">
            {sent ? 'Solicitud enviada' : 'Recuperar contraseña'}
          </h1>
          <p className="mt-1 text-sm text-text-secondary">
            {sent
              ? 'El administrador revisará tu solicitud'
              : 'Para dueños de negocio'}
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6">
          {sent ? (
            <div className="space-y-4 text-center">
              <p className="text-sm text-text-secondary">
                Si el correo corresponde a un negocio, registramos tu solicitud. El administrador
                verificará tu identidad y te entregará una <strong className="text-text-primary">contraseña
                nueva</strong>. Luego podrás cambiarla desde tu panel.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                <ArrowLeft className="h-4 w-4" /> Volver a iniciar sesión
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
                  {error}
                </div>
              )}
              <div>
                <label htmlFor="forgot-email" className="mb-1 block text-sm font-medium text-text-secondary">
                  Correo de tu cuenta
                </label>
                <input
                  id="forgot-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-text-primary outline-none focus:border-primary"
                  placeholder="tu@negocio.pe"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary/20 transition hover:bg-primary/90 disabled:opacity-60"
              >
                {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                Enviar solicitud
              </button>
              <Link
                to="/login"
                className="flex items-center justify-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
              >
                <ArrowLeft className="h-4 w-4" /> Volver a iniciar sesión
              </Link>
            </form>
          )}
        </div>
      </motion.div>
    </div>
  )
}
