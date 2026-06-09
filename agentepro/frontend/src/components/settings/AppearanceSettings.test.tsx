import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AppearanceSettings } from './AppearanceSettings'
import { useThemeStore } from '../../stores/theme.store'
import { useUIStore } from '../../stores/ui.store'

beforeEach(() => {
  useThemeStore.setState({ mode: 'dark', brandColor: null, userId: null, byUser: {} })
  useUIStore.setState({ toasts: [], sidebarCollapsed: false })
})

describe('AppearanceSettings', () => {
  it('cambiar a modo claro actualiza el store', async () => {
    const user = userEvent.setup()
    render(<AppearanceSettings />)
    await user.click(screen.getByRole('button', { name: /Claro/ }))
    expect(useThemeStore.getState().mode).toBe('light')
  })

  it('elegir un color de marca lo guarda', async () => {
    const user = userEvent.setup()
    render(<AppearanceSettings />)
    // El primer swatch corresponde al primer preset (#10B981)
    const swatches = screen.getAllByTitle(/^#/)
    await user.click(swatches[1])
    expect(useThemeStore.getState().brandColor).toBeTruthy()
  })

  it('el selector de color personalizado dispara setBrandColor', () => {
    render(<AppearanceSettings />)
    const colorInput = document.querySelector('input[type="color"]') as HTMLInputElement
    fireEvent.change(colorInput, { target: { value: '#123456' } })
    expect(useThemeStore.getState().brandColor).toBe('#123456')
  })

  it('el botón Restablecer aparece con color y lo limpia, mostrando un toast', async () => {
    const user = userEvent.setup()
    useThemeStore.setState({ brandColor: '#EF4444' })
    render(<AppearanceSettings />)
    await user.click(screen.getByRole('button', { name: /Restablecer/ }))
    expect(useThemeStore.getState().brandColor).toBeNull()
    expect(useUIStore.getState().toasts.some((t) => t.title === 'Color restablecido')).toBe(true)
  })

  it('sin color de marca no muestra el botón Restablecer', () => {
    render(<AppearanceSettings />)
    expect(screen.queryByRole('button', { name: /Restablecer/ })).not.toBeInTheDocument()
  })
})
