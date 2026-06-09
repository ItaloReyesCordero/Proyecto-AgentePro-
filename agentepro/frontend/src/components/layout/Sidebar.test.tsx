import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

const get = vi.fn()
vi.mock('../../lib/api', () => ({ api: { get: (...a: unknown[]) => get(...a) } }))

const navigate = vi.fn()
vi.mock('react-router-dom', async (orig) => {
  const actual = await orig<typeof import('react-router-dom')>()
  return { ...actual, useNavigate: () => navigate }
})

import { Sidebar } from './Sidebar'
import { renderWithProviders } from '../../test/utils'
import { useAuthStore } from '../../stores/auth.store'
import { useUIStore } from '../../stores/ui.store'

beforeEach(() => {
  get.mockReset()
  navigate.mockReset()
  useAuthStore.setState({ token: 't', refreshToken: null, user: { id: 'u', email: 'e', full_name: 'N', role: 'owner', tenant_id: 't' } })
  useUIStore.setState({ toasts: [], sidebarCollapsed: false })
})

describe('Sidebar', () => {
  it('owner ve solo los módulos de su plan', async () => {
    get.mockResolvedValue({ data: { features: ['voice'] } })
    renderWithProviders(<Sidebar />, { route: '/app' })
    expect(await screen.findByText('Llamadas')).toBeInTheDocument() // feature voice
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.queryByText('Instagram')).not.toBeInTheDocument() // feature instagram no incluida
  })

  it('superadmin solo ve el panel de admin', async () => {
    useAuthStore.setState({ user: { id: 'u', email: 'e', full_name: 'N', role: 'superadmin', tenant_id: null } })
    get.mockResolvedValue({ data: { features: [] } })
    renderWithProviders(<Sidebar />, { route: '/app/admin' })
    expect(await screen.findByText('Super Admin')).toBeInTheDocument()
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
  })

  it('clic en el logo navega a /app', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { features: [] } })
    renderWithProviders(<Sidebar />, { route: '/app' })
    await user.click(screen.getByRole('img', { name: 'AgentePro' }))
    expect(navigate).toHaveBeenCalledWith('/app')
  })

  it('el botón de colapsar alterna el estado', async () => {
    const user = userEvent.setup()
    get.mockResolvedValue({ data: { features: [] } })
    renderWithProviders(<Sidebar />, { route: '/app' })
    await user.click(screen.getByTitle('Colapsar'))
    expect(useUIStore.getState().sidebarCollapsed).toBe(true)
  })

  it('colapsada muestra el ícono de expandir', async () => {
    useUIStore.setState({ sidebarCollapsed: true })
    get.mockResolvedValue({ data: { features: [] } })
    renderWithProviders(<Sidebar />, { route: '/app' })
    expect(await screen.findByTitle('Expandir')).toBeInTheDocument()
  })
})
