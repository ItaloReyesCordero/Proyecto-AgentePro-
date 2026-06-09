import { describe, it, expect, vi, beforeEach } from 'vitest'

const post = vi.fn()
const get = vi.fn()

vi.mock('./api', () => ({
  api: {
    post: (...args: unknown[]) => post(...args),
    get: (...args: unknown[]) => get(...args),
  },
}))

import { login, register, getMe } from './auth'

describe('auth lib', () => {
  beforeEach(() => {
    post.mockReset()
    get.mockReset()
  })

  it('login envía username/password como form-urlencoded', async () => {
    post.mockResolvedValue({ data: { access_token: 'a', refresh_token: 'r', token_type: 'bearer' } })
    const res = await login({ username: 'u@x.com', password: 'secret' })
    expect(res.access_token).toBe('a')
    const [url, body, config] = post.mock.calls[0]
    expect(url).toBe('/auth/login')
    expect(body).toBeInstanceOf(URLSearchParams)
    expect((body as URLSearchParams).get('username')).toBe('u@x.com')
    expect((body as URLSearchParams).get('password')).toBe('secret')
    expect((config as { headers: Record<string, string> }).headers['Content-Type']).toBe(
      'application/x-www-form-urlencoded',
    )
  })

  it('register hace POST /auth/register con el payload', async () => {
    post.mockResolvedValue({ data: { access_token: 'a', refresh_token: 'r', token_type: 'bearer' } })
    const data = { email: 'e@x.com', password: 'p', full_name: 'N', business_name: 'B' }
    const res = await register(data)
    expect(res.refresh_token).toBe('r')
    expect(post).toHaveBeenCalledWith('/auth/register', data)
  })

  it('getMe hace GET /auth/me y devuelve el perfil', async () => {
    const profile = { id: '1', email: 'e@x.com', full_name: 'N', role: 'owner', tenant_id: 't' }
    get.mockResolvedValue({ data: profile })
    const res = await getMe()
    expect(res).toEqual(profile)
    expect(get).toHaveBeenCalledWith('/auth/me')
  })
})
