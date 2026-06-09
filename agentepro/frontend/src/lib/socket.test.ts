import { describe, it, expect, vi, beforeEach } from 'vitest'

const fakeSocket = { disconnect: vi.fn() }
const io = vi.fn((..._args: unknown[]) => fakeSocket)

vi.mock('socket.io-client', () => ({
  io: (...args: unknown[]) => io(...args),
  Socket: class {},
}))

import { getSocket, disconnectSocket } from './socket'
import { useAuthStore } from '../stores/auth.store'

describe('socket lib', () => {
  beforeEach(() => {
    disconnectSocket()
    io.mockClear()
    fakeSocket.disconnect.mockClear()
    useAuthStore.setState({ token: 'mi-token', refreshToken: null, user: null })
  })

  it('getSocket crea el socket una sola vez (singleton) con el token de auth', () => {
    const s1 = getSocket()
    const s2 = getSocket()
    expect(s1).toBe(s2)
    expect(io).toHaveBeenCalledTimes(1)
    const [path, opts] = io.mock.calls[0] as unknown as [string, { auth: { token: string | null } }]
    expect(path).toBe('/')
    expect(opts.auth.token).toBe('mi-token')
  })

  it('disconnectSocket desconecta y permite recrear el socket', () => {
    const s1 = getSocket()
    disconnectSocket()
    expect(fakeSocket.disconnect).toHaveBeenCalledTimes(1)
    getSocket()
    expect(io).toHaveBeenCalledTimes(2)
    void s1
  })

  it('disconnectSocket sin socket activo no falla', () => {
    expect(() => disconnectSocket()).not.toThrow()
  })
})
