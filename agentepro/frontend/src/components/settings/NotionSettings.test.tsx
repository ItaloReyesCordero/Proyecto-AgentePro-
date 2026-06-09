import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AxiosError } from 'axios'

const get = vi.fn()
const post = vi.fn()
vi.mock('../../lib/api', async (orig) => {
  const actual = await orig<typeof import('../../lib/api')>()
  return { ...actual, api: { get: (...a: unknown[]) => get(...a), post: (...a: unknown[]) => post(...a) } }
})

import { NotionSettings } from './NotionSettings'
import { renderWithProviders } from '../../test/utils'
import { useUIStore } from '../../stores/ui.store'

beforeEach(() => {
  get.mockReset()
  post.mockReset()
  useUIStore.setState({ toasts: [], sidebarCollapsed: false })
})

describe('NotionSettings', () => {
  it('muestra el spinner de carga inicial', () => {
    get.mockReturnValue(new Promise(() => {}))
    const { container } = renderWithProviders(<NotionSettings />)
    expect(container.querySelector('.animate-spin')).toBeTruthy()
  })

  it('desconectado: muestra el formulario y conecta', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { connected: false, database_id: null, last_synced_at: null, services_count: 0 } })
    post.mockResolvedValue({ data: { synced: 5, last_synced_at: null } })
    renderWithProviders(<NotionSettings />)

    const token = await screen.findByLabelText(/Token de integración/)
    const dbId = screen.getByLabelText(/ID o enlace/)
    const connectBtn = screen.getByRole('button', { name: /Conectar y sincronizar/ })
    expect(connectBtn).toBeDisabled()

    await user.type(token, 'secret_abc')
    await user.type(dbId, 'db-123')
    expect(connectBtn).toBeEnabled()
    await user.click(connectBtn)

    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/notion/connect', { api_key: 'secret_abc', database_id: 'db-123' }),
    )
    await waitFor(() =>
      expect(useUIStore.getState().toasts.some((t) => /5 servicios/.test(t.title))).toBe(true),
    )
  })

  it('error al conectar muestra toast de error', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { connected: false, database_id: null, last_synced_at: null, services_count: 0 } })
    post.mockRejectedValue(new AxiosError('boom'))
    renderWithProviders(<NotionSettings />)

    await user.type(await screen.findByLabelText(/Token de integración/), 'k')
    await user.type(screen.getByLabelText(/ID o enlace/), 'd')
    await user.click(screen.getByRole('button', { name: /Conectar y sincronizar/ }))

    await waitFor(() =>
      expect(useUIStore.getState().toasts.some((t) => t.variant === 'error')).toBe(true),
    )
  })

  it('conectado: muestra estado y permite sincronizar', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { connected: true, database_id: 'db', last_synced_at: '2024-01-01T00:00:00Z', services_count: 7 } })
    post.mockResolvedValue({ data: { synced: 3, last_synced_at: '2024-02-01T00:00:00Z' } })
    renderWithProviders(<NotionSettings />)

    expect(await screen.findByText('Conectado')).toBeInTheDocument()
    expect(screen.getByText('7')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /Sincronizar ahora/ }))
    await waitFor(() => expect(post).toHaveBeenCalledWith('/notion/sync', {}))
    await waitFor(() =>
      expect(useUIStore.getState().toasts.some((t) => /3 servicios/.test(t.title))).toBe(true),
    )
  })

  it('conectado sin última sincronización muestra guion', async () => {
    get.mockResolvedValue({ data: { connected: true, database_id: 'db', last_synced_at: null, services_count: 0 } })
    renderWithProviders(<NotionSettings />)
    expect(await screen.findByText('—')).toBeInTheDocument()
  })

  it('desconectar dispara el endpoint y notifica', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { connected: true, database_id: 'db', last_synced_at: null, services_count: 1 } })
    post.mockResolvedValue({ data: {} })
    renderWithProviders(<NotionSettings />)
    await user.click(await screen.findByRole('button', { name: /Desconectar/ }))
    await waitFor(() => expect(post).toHaveBeenCalledWith('/notion/disconnect', {}))
    await waitFor(() =>
      expect(useUIStore.getState().toasts.some((t) => t.title === 'Notion desconectado')).toBe(true),
    )
  })

  it('error al sincronizar muestra toast de error', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { connected: true, database_id: 'db', last_synced_at: null, services_count: 1 } })
    post.mockRejectedValue(new AxiosError('x'))
    renderWithProviders(<NotionSettings />)
    await user.click(await screen.findByRole('button', { name: /Sincronizar ahora/ }))
    await waitFor(() =>
      expect(useUIStore.getState().toasts.some((t) => t.variant === 'error')).toBe(true),
    )
  })

  it('error al desconectar muestra toast de error', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { connected: true, database_id: 'db', last_synced_at: null, services_count: 1 } })
    post.mockRejectedValue(new AxiosError('x'))
    renderWithProviders(<NotionSettings />)
    await user.click(await screen.findByRole('button', { name: /Desconectar/ }))
    await waitFor(() =>
      expect(useUIStore.getState().toasts.some((t) => t.variant === 'error')).toBe(true),
    )
  })
})
