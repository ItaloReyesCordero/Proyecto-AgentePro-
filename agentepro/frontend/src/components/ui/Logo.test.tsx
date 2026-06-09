import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Logo, LogoMark } from './Logo'

describe('Logo', () => {
  it('LogoMark renderiza un SVG con etiqueta accesible', () => {
    render(<LogoMark />)
    expect(screen.getByRole('img', { name: 'AgentePro' })).toBeInTheDocument()
  })

  it('LogoMark acepta tamaño personalizado', () => {
    render(<LogoMark size={64} className="extra" />)
    const svg = screen.getByRole('img')
    expect(svg).toHaveAttribute('width', '64')
    expect(svg).toHaveClass('extra')
  })

  it('Logo sin texto no muestra el wordmark', () => {
    render(<Logo />)
    expect(screen.queryByText('AgentePro')).not.toBeInTheDocument()
  })

  it('Logo con showText muestra el wordmark', () => {
    render(<Logo showText textClassName="wm" className="cont" />)
    expect(screen.getByText('AgentePro')).toBeInTheDocument()
  })
})
