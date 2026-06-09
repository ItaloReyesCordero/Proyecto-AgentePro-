import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'

const get = vi.fn()
vi.mock('../../lib/api', () => ({ api: { get: (...a: unknown[]) => get(...a) } }))

import { AppLayout } from './AppLayout'
import { makeQueryClient } from '../../test/utils'
import { QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '../../stores/auth.store'

function renderAt(path: string) {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/app" element={<AppLayout />}>
            <Route index element={<div>Contenido Dashboard</div>} />
          </Route>
          <Route path="/app/admin" element={<div>Panel Admin</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  get.mockReset()
  get.mockResolvedValue({ data: { features: [], plan: 'pro', trial_ends_at: null, payment_state: 'ok', payment_due_at: null } })
})

describe('AppLayout', () => {
  it('owner ve el layout con el contenido (Outlet) y el TrialBanner', () => {
    useAuthStore.setState({ token: 't', refreshToken: null, user: { id: 'u', email: 'e', full_name: 'N', role: 'owner', tenant_id: 't' } })
    renderAt('/app')
    expect(screen.getByText('Contenido Dashboard')).toBeInTheDocument()
  })

  it('superadmin en una ruta de negocio es redirigido a /app/admin', () => {
    useAuthStore.setState({ token: 't', refreshToken: null, user: { id: 'u', email: 'e', full_name: 'N', role: 'superadmin', tenant_id: null } })
    renderAt('/app')
    expect(screen.getByText('Panel Admin')).toBeInTheDocument()
    expect(screen.queryByText('Contenido Dashboard')).not.toBeInTheDocument()
  })
})
