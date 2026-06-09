import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusBadge } from './StatusBadge'

describe('StatusBadge', () => {
  it('muestra la etiqueta configurada para un estado conocido', () => {
    render(<StatusBadge status="open" />)
    expect(screen.getByText('Abierta')).toBeInTheDocument()
  })

  it('mapea otra variante (lead stage)', () => {
    render(<StatusBadge status="hot" />)
    expect(screen.getByText('Caliente')).toBeInTheDocument()
  })

  it('para un estado desconocido usa el texto crudo y estilo por defecto', () => {
    render(<StatusBadge status={'desconocido' as never} className="extra" />)
    const badge = screen.getByText('desconocido')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('extra')
  })
})
