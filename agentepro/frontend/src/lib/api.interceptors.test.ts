import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { api } from './api'
import { useAuthStore } from '../stores/auth.store'

// Accede a los handlers registrados en el interceptor de la instancia de axios.
type Handler<T> = { fulfilled: (v: T) => unknown; rejected?: (e: unknown) => unknown }
const reqHandlers = (api.interceptors.request as unknown as { handlers: Handler<InternalAxiosRequestConfig>[] }).handlers
const resHandlers = (api.interceptors.response as unknown as { handlers: Handler<unknown>[] }).handlers

function axiosErr(status: number, data?: unknown): AxiosError {
  return new AxiosError('fail', 'ERR', undefined, undefined, {
    data,
    status,
    statusText: '',
    headers: {},
    config: {} as never,
  })
}

describe('api request interceptor', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, refreshToken: null, user: null })
  })

  it('agrega el header Authorization cuando hay token', () => {
    useAuthStore.setState({ token: 'abc', refreshToken: null, user: null })
    const config = { headers: {} } as unknown as InternalAxiosRequestConfig
    const out = reqHandlers[0].fulfilled(config) as InternalAxiosRequestConfig
    expect(out.headers.Authorization).toBe('Bearer abc')
  })

  it('no agrega Authorization cuando no hay token', () => {
    const config = { headers: {} } as unknown as InternalAxiosRequestConfig
    const out = reqHandlers[0].fulfilled(config) as InternalAxiosRequestConfig
    expect(out.headers.Authorization).toBeUndefined()
  })
})

describe('api response interceptor', () => {
  const originalLocation = window.location
  let logoutSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    // jsdom: reemplaza location por un objeto mutable.
    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: { href: '', pathname: '/app' },
    })
    logoutSpy = vi.spyOn(useAuthStore.getState(), 'logout')
  })

  afterEach(() => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: originalLocation,
    })
    logoutSpy.mockRestore()
  })

  it('deja pasar las respuestas exitosas', () => {
    const resp = { data: 'ok' }
    expect(resHandlers[0].fulfilled(resp)).toBe(resp)
  })

  it('en 401 hace logout y redirige a /login', async () => {
    await expect(resHandlers[0].rejected!(axiosErr(401))).rejects.toBeTruthy()
    expect(logoutSpy).toHaveBeenCalled()
    expect(window.location.href).toBe('/login')
  })

  it('en 402 TRIAL_EXPIRED redirige a /app/upgrade', async () => {
    await expect(resHandlers[0].rejected!(axiosErr(402, { code: 'TRIAL_EXPIRED' }))).rejects.toBeTruthy()
    expect(window.location.href).toBe('/app/upgrade')
  })

  it('en 402 PAYMENT_OVERDUE redirige a /app/upgrade', async () => {
    await expect(resHandlers[0].rejected!(axiosErr(402, { code: 'PAYMENT_OVERDUE' }))).rejects.toBeTruthy()
    expect(window.location.href).toBe('/app/upgrade')
  })

  it('en 402 no redirige si ya está en /app/upgrade', async () => {
    window.location.pathname = '/app/upgrade'
    await expect(resHandlers[0].rejected!(axiosErr(402, { code: 'ACCOUNT_SUSPENDED' }))).rejects.toBeTruthy()
    expect(window.location.href).toBe('')
  })

  it('en 402 con código desconocido no redirige', async () => {
    await expect(resHandlers[0].rejected!(axiosErr(402, { code: 'OTRO' }))).rejects.toBeTruthy()
    expect(window.location.href).toBe('')
  })

  it('en 500 no hace logout ni redirige', async () => {
    await expect(resHandlers[0].rejected!(axiosErr(500))).rejects.toBeTruthy()
    expect(logoutSpy).not.toHaveBeenCalled()
    expect(window.location.href).toBe('')
  })

  it('con un error que no es de axios solo lo re-lanza', async () => {
    const err = new Error('boom')
    await expect(resHandlers[0].rejected!(err)).rejects.toBe(err)
    expect(logoutSpy).not.toHaveBeenCalled()
  })
})
