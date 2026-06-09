import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'

type Listener = (...args: unknown[]) => void
const handlers: Record<string, Listener> = {}
const on = vi.fn((event: string, cb: Listener) => { handlers[event] = cb })
const off = vi.fn()
const fakeSocket = { id: 'sock-1', on, off }
const getSocket = vi.fn(() => fakeSocket)
const disconnectSocket = vi.fn()

vi.mock('../lib/socket', () => ({
  getSocket: () => getSocket(),
  disconnectSocket: () => disconnectSocket(),
}))

const invalidateQueries = vi.fn()
vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({ invalidateQueries }),
}))

const addToast = vi.fn()
vi.mock('../stores/ui.store', () => ({
  useUIStore: (selector: (s: { addToast: typeof addToast }) => unknown) =>
    selector({ addToast }),
}))

let token: string | null = 'tok'
vi.mock('../stores/auth.store', () => ({
  useAuthStore: () => ({ token }),
}))

import { useSocket } from './useSocket'

describe('useSocket', () => {
  beforeEach(() => {
    Object.keys(handlers).forEach((k) => delete handlers[k])
    on.mockClear(); off.mockClear(); getSocket.mockClear(); disconnectSocket.mockClear()
    invalidateQueries.mockClear(); addToast.mockClear()
    token = 'tok'
    vi.spyOn(console, 'log').mockImplementation(() => {})
  })

  it('sin token no conecta el socket', () => {
    token = null
    renderHook(() => useSocket())
    expect(getSocket).not.toHaveBeenCalled()
    expect(disconnectSocket).toHaveBeenCalled()
  })

  it('con token registra los listeners', () => {
    renderHook(() => useSocket())
    expect(getSocket).toHaveBeenCalled()
    expect(handlers).toHaveProperty('new_message')
    expect(handlers).toHaveProperty('escalation')
    expect(handlers).toHaveProperty('call_completed')
  })

  it('connect/disconnect loguean', () => {
    renderHook(() => useSocket())
    handlers.connect()
    handlers.disconnect()
    expect(console.log).toHaveBeenCalled()
  })

  it('new_message de un contacto invalida queries y notifica', () => {
    renderHook(() => useSocket())
    handlers.new_message({ conversation_id: 'c1', message: { sender_type: 'contact' } })
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['messages', 'c1'] })
    expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Nuevo mensaje' }))
  })

  it('new_message del bot no notifica', () => {
    renderHook(() => useSocket())
    handlers.new_message({ conversation_id: 'c1', message: { sender_type: 'ai' } })
    expect(addToast).not.toHaveBeenCalled()
  })

  it('escalation notifica con warning', () => {
    renderHook(() => useSocket())
    handlers.escalation()
    expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'warning' }))
  })

  it('conversation_updated invalida queries', () => {
    renderHook(() => useSocket())
    handlers.conversation_updated({ conversation_id: 'c2' })
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['conversations', 'c2'] })
  })

  it('call_started invalida calls', () => {
    renderHook(() => useSocket())
    handlers.call_started()
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['calls'] })
  })

  it('call_completed notifica éxito', () => {
    renderHook(() => useSocket())
    handlers.call_completed()
    expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'success' }))
  })

  it('instagram_post_ready notifica', () => {
    renderHook(() => useSocket())
    handlers.instagram_post_ready()
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['instagram-posts'] })
    expect(addToast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Posts generados' }))
  })

  it('al desmontar quita los listeners', () => {
    const { unmount } = renderHook(() => useSocket())
    unmount()
    expect(off).toHaveBeenCalledWith('new_message')
  })
})
