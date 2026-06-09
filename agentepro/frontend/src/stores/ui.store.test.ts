import { describe, it, expect, beforeEach } from 'vitest'
import { useUIStore, toast } from './ui.store'

describe('useUIStore', () => {
  beforeEach(() => {
    useUIStore.setState({ toasts: [], sidebarCollapsed: false })
  })

  it('addToast agrega un toast con id generado', () => {
    useUIStore.getState().addToast({ title: 'Hola', variant: 'success' })
    const { toasts } = useUIStore.getState()
    expect(toasts).toHaveLength(1)
    expect(toasts[0].title).toBe('Hola')
    expect(toasts[0].variant).toBe('success')
    expect(typeof toasts[0].id).toBe('string')
    expect(toasts[0].id.length).toBeGreaterThan(0)
  })

  it('removeToast elimina por id', () => {
    useUIStore.getState().addToast({ title: 'A', variant: 'default' })
    useUIStore.getState().addToast({ title: 'B', variant: 'error' })
    const firstId = useUIStore.getState().toasts[0].id
    useUIStore.getState().removeToast(firstId)
    const { toasts } = useUIStore.getState()
    expect(toasts).toHaveLength(1)
    expect(toasts[0].title).toBe('B')
  })

  it('toggleSidebar alterna el estado colapsado', () => {
    expect(useUIStore.getState().sidebarCollapsed).toBe(false)
    useUIStore.getState().toggleSidebar()
    expect(useUIStore.getState().sidebarCollapsed).toBe(true)
    useUIStore.getState().toggleSidebar()
    expect(useUIStore.getState().sidebarCollapsed).toBe(false)
  })

  it('el helper toast() agrega al store', () => {
    toast({ title: 'Externo', variant: 'warning' })
    const { toasts } = useUIStore.getState()
    expect(toasts).toHaveLength(1)
    expect(toasts[0].title).toBe('Externo')
  })
})
