import axios from 'axios'
import { useAuthStore } from '../stores/auth.store'

/**
 * Extrae un mensaje legible de un error de axios. FastAPI devuelve `detail`
 * como string (HTTPException) o como array de objetos (errores de validación
 * 422); renderizar ese array directamente rompe React, así que lo aplanamos.
 */
export function apiErrorMessage(err: unknown, fallback = 'Ocurrió un error'): string {
  if (!axios.isAxiosError(err)) return fallback
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const msgs = detail
      .map((d: { msg?: string }) => (typeof d?.msg === 'string' ? d.msg : null))
      .filter(Boolean)
    if (msgs.length) return msgs.join(' · ')
  }
  return err.message || fallback
}

export const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const code = (error.response?.data as { code?: string } | undefined)?.code
      if (status === 401) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      } else if (
        status === 402 &&
        (code === 'TRIAL_EXPIRED' || code === 'PAYMENT_OVERDUE' || code === 'ACCOUNT_SUSPENDED') &&
        window.location.pathname !== '/app/upgrade'
      ) {
        // Trial vencido, suspensión por falta de pago, o cuenta desactivada por
        // el administrador: el backend bloquea; llevamos al cliente a la pantalla
        // de contacto/pago en vez de dejarlo con un dashboard a medias.
        window.location.href = '/app/upgrade'
      }
    }
    return Promise.reject(error)
  },
)
