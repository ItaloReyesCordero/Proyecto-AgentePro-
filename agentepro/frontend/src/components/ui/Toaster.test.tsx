import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Toaster } from './Toaster'
import { useUIStore } from '../../stores/ui.store'

describe('Toaster', () => {
  beforeEach(() => {
    useUIStore.setState({ toasts: [], sidebarCollapsed: false })
  })

  it('no muestra nada sin toasts', () => {
    render(<Toaster />)
    expect(screen.queryByText(/./)).toBeNull()
  })

  it('renderiza cada variante con título y descripción', () => {
    useUIStore.setState({
      toasts: [
        { id: '1', title: 'OK', description: 'detalle', variant: 'success' },
        { id: '2', title: 'Err', variant: 'error' },
        { id: '3', title: 'Aviso', variant: 'warning' },
        { id: '4', title: 'Info', variant: 'default' },
      ],
    })
    render(<Toaster />)
    expect(screen.getByText('OK')).toBeInTheDocument()
    expect(screen.getByText('detalle')).toBeInTheDocument()
    expect(screen.getByText('Err')).toBeInTheDocument()
    expect(screen.getByText('Aviso')).toBeInTheDocument()
    expect(screen.getByText('Info')).toBeInTheDocument()
  })

  it('el botón de cerrar elimina el toast', async () => {
    const user = userEvent.setup()
    useUIStore.setState({ toasts: [{ id: '9', title: 'Cierra', variant: 'default' }] })
    render(<Toaster />)
    const closeBtn = screen.getAllByRole('button')[0]
    await user.click(closeBtn)
    expect(useUIStore.getState().toasts).toHaveLength(0)
  })

  describe('auto-cierre', () => {
    beforeEach(() => vi.useFakeTimers())
    afterEach(() => vi.useRealTimers())

    it('se cierra solo tras el timeout', () => {
      useUIStore.setState({ toasts: [{ id: 't', title: 'Auto', variant: 'default' }] })
      render(<Toaster />)
      expect(useUIStore.getState().toasts).toHaveLength(1)
      act(() => { vi.advanceTimersByTime(4600) })
      expect(useUIStore.getState().toasts).toHaveLength(0)
    })
  })
})
