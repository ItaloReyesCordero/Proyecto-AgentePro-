import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'

const navigate = vi.fn()
vi.mock('react-router-dom', async (orig) => {
  const actual = await orig<typeof import('react-router-dom')>()
  return { ...actual, useNavigate: () => navigate }
})

import { TopBar } from './TopBar'
import { useAuthStore } from '../../stores/auth.store'
import { useThemeStore } from '../../stores/theme.store'

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <TopBar />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  navigate.mockReset()
  useAuthStore.setState({ token: 't', refreshToken: null, user: { id: 'u', email: 'ada@x.com', full_name: 'Ada Lovelace', role: 'owner', tenant_id: 't' } })
  useThemeStore.setState({ mode: 'dark', brandColor: null, userId: null, byUser: {} })
})

describe('TopBar', () => {
  it('muestra el título de la página según la ruta', () => {
    renderAt('/app/conversations')
    expect(screen.getByText('Conversaciones')).toBeInTheDocument()
  })

  it('rutas desconocidas usan "AgentePro"', () => {
    renderAt('/app/loquesea')
    expect(screen.getByText('AgentePro')).toBeInTheDocument()
  })

  it('muestra las iniciales del usuario', () => {
    renderAt('/app')
    expect(screen.getByText('AL')).toBeInTheDocument()
  })

  it('sin nombre usa iniciales por defecto AP', () => {
    useAuthStore.setState({ user: { id: 'u', email: 'e', full_name: '', role: 'owner', tenant_id: 't' } })
    renderAt('/app')
    expect(screen.getByText('AP')).toBeInTheDocument()
  })

  it('el toggle de tema alterna el modo', async () => {
    const user = userEvent.setup()
    renderAt('/app')
    await user.click(screen.getByLabelText('Cambiar tema'))
    expect(useThemeStore.getState().mode).toBe('light')
  })

  it('abre el menú y permite ir a Perfil', async () => {
    const user = userEvent.setup()
    renderAt('/app')
    await user.click(screen.getByText('Ada Lovelace'))
    await user.click(screen.getByText('Perfil'))
    expect(navigate).toHaveBeenCalledWith('/app/settings')
  })

  it('cerrar sesión hace logout y navega a /login', async () => {
    const user = userEvent.setup()
    renderAt('/app')
    await user.click(screen.getByText('Ada Lovelace'))
    await user.click(screen.getByText('Cerrar sesión'))
    expect(navigate).toHaveBeenCalledWith('/login')
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('superadmin no ve la opción Perfil', async () => {
    useAuthStore.setState({ user: { id: 'u', email: 'e', full_name: 'Super Admin', role: 'superadmin', tenant_id: null } })
    const user = userEvent.setup()
    renderAt('/app')
    await user.click(screen.getByText('Super Admin'))
    expect(screen.queryByText('Perfil')).not.toBeInTheDocument()
  })

  it('el overlay cierra el menú con Enter/clic', async () => {
    const user = userEvent.setup()
    renderAt('/app')
    await user.click(screen.getByText('Ada Lovelace'))
    const overlay = screen.getByLabelText('Cerrar menú')
    overlay.focus()
    await user.keyboard('{Enter}')
    expect(screen.queryByText('Cerrar sesión')).not.toBeInTheDocument()
  })

  it('modo claro muestra el ícono de luna para volver a oscuro', () => {
    useThemeStore.setState({ mode: 'light' })
    renderAt('/app')
    expect(screen.getByTitle('Cambiar a modo oscuro')).toBeInTheDocument()
  })
})
