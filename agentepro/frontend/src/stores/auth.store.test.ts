import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore, type User } from './auth.store'

const user: User = {
  id: 'u1',
  email: 'a@b.com',
  full_name: 'Ada Lovelace',
  role: 'owner',
  tenant_id: 't1',
}

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, refreshToken: null, user: null })
  })

  it('arranca sin sesión', () => {
    const s = useAuthStore.getState()
    expect(s.token).toBeNull()
    expect(s.refreshToken).toBeNull()
    expect(s.user).toBeNull()
  })

  it('setAuth guarda token, refreshToken y user', () => {
    useAuthStore.getState().setAuth('tok', 'ref', user)
    const s = useAuthStore.getState()
    expect(s.token).toBe('tok')
    expect(s.refreshToken).toBe('ref')
    expect(s.user).toEqual(user)
  })

  it('logout limpia la sesión', () => {
    useAuthStore.getState().setAuth('tok', 'ref', user)
    useAuthStore.getState().logout()
    const s = useAuthStore.getState()
    expect(s.token).toBeNull()
    expect(s.refreshToken).toBeNull()
    expect(s.user).toBeNull()
  })
})
