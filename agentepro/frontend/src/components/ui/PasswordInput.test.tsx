import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PasswordInput } from './PasswordInput'

describe('PasswordInput', () => {
  it('arranca oculto (type=password) y muestra placeholder', () => {
    render(<PasswordInput placeholder="Contraseña" />)
    const input = screen.getByPlaceholderText('Contraseña')
    expect(input).toHaveAttribute('type', 'password')
  })

  it('el botón alterna visible/oculto', async () => {
    const user = userEvent.setup()
    render(<PasswordInput placeholder="pwd" />)
    const input = screen.getByPlaceholderText('pwd')
    const toggle = screen.getByRole('button', { name: 'Mostrar contraseña' })

    await user.click(toggle)
    expect(input).toHaveAttribute('type', 'text')
    expect(screen.getByRole('button', { name: 'Ocultar contraseña' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Ocultar contraseña' }))
    expect(input).toHaveAttribute('type', 'password')
  })

  it('usa la clase por defecto y añade pr-10', () => {
    render(<PasswordInput placeholder="x" />)
    expect(screen.getByPlaceholderText('x')).toHaveClass('input-base', 'pr-10')
  })

  it('acepta una clase personalizada', () => {
    render(<PasswordInput placeholder="y" className="custom" />)
    expect(screen.getByPlaceholderText('y')).toHaveClass('custom', 'pr-10')
  })
})
