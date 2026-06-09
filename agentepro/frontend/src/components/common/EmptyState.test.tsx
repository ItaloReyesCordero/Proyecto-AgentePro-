import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Inbox } from 'lucide-react'

let reduced = false
vi.mock('framer-motion', async (orig) => {
  const actual = await orig<typeof import('framer-motion')>()
  return { ...actual, useReducedMotion: () => reduced }
})

import { EmptyState } from './EmptyState'

describe('EmptyState', () => {
  it('muestra título (con animación)', () => {
    reduced = false
    render(<EmptyState icon={Inbox} title="Sin datos" />)
    expect(screen.getByText('Sin datos')).toBeInTheDocument()
  })

  it('muestra descripción y acción cuando se pasan', () => {
    render(
      <EmptyState
        icon={Inbox}
        title="Vacío"
        description="No hay nada aquí"
        action={<button>Crear</button>}
        className="extra"
      />,
    )
    expect(screen.getByText('No hay nada aquí')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Crear' })).toBeInTheDocument()
  })

  it('respeta prefers-reduced-motion (sin animación de flotar)', () => {
    reduced = true
    render(<EmptyState icon={Inbox} title="Reducido" />)
    expect(screen.getByText('Reducido')).toBeInTheDocument()
  })
})
