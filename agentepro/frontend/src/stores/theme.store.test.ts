import { describe, it, expect, beforeEach } from 'vitest'
import { useThemeStore, BRAND_PRESETS } from './theme.store'

function reset() {
  useThemeStore.setState({ mode: 'dark', brandColor: null, userId: null, byUser: {} })
}

describe('useThemeStore', () => {
  beforeEach(reset)

  it('exporta presets de marca', () => {
    expect(BRAND_PRESETS[0]).toBe('#10B981')
    expect(BRAND_PRESETS.length).toBeGreaterThan(0)
  })

  it('arranca en modo oscuro sin color', () => {
    const s = useThemeStore.getState()
    expect(s.mode).toBe('dark')
    expect(s.brandColor).toBeNull()
  })

  it('setMode cambia el modo (sin usuario no persiste en byUser)', () => {
    useThemeStore.getState().setMode('light')
    const s = useThemeStore.getState()
    expect(s.mode).toBe('light')
    expect(s.byUser).toEqual({})
  })

  it('toggleMode alterna dark <-> light', () => {
    useThemeStore.getState().toggleMode()
    expect(useThemeStore.getState().mode).toBe('light')
    useThemeStore.getState().toggleMode()
    expect(useThemeStore.getState().mode).toBe('dark')
  })

  it('setBrandColor sin usuario no guarda en byUser', () => {
    useThemeStore.getState().setBrandColor('#3B82F6')
    const s = useThemeStore.getState()
    expect(s.brandColor).toBe('#3B82F6')
    expect(s.byUser).toEqual({})
  })

  it('con usuario, setMode y setBrandColor persisten por usuario', () => {
    useThemeStore.getState().loadForUser('user-1')
    useThemeStore.getState().setMode('light')
    useThemeStore.getState().setBrandColor('#EC4899')
    const s = useThemeStore.getState()
    expect(s.byUser['user-1']).toEqual({ mode: 'light', brandColor: '#EC4899' })
  })

  it('loadForUser(null) restablece el tema por defecto', () => {
    useThemeStore.getState().loadForUser('user-1')
    useThemeStore.getState().setMode('light')
    useThemeStore.getState().loadForUser(null)
    const s = useThemeStore.getState()
    expect(s.userId).toBeNull()
    expect(s.mode).toBe('dark')
    expect(s.brandColor).toBeNull()
  })

  it('loadForUser carga las preferencias guardadas del usuario', () => {
    useThemeStore.setState({ byUser: { bob: { mode: 'light', brandColor: '#F59E0B' } } })
    useThemeStore.getState().loadForUser('bob')
    const s = useThemeStore.getState()
    expect(s.userId).toBe('bob')
    expect(s.mode).toBe('light')
    expect(s.brandColor).toBe('#F59E0B')
  })

  it('loadForUser usa valores por defecto si el usuario no tiene preferencias', () => {
    useThemeStore.getState().loadForUser('nuevo')
    const s = useThemeStore.getState()
    expect(s.mode).toBe('dark')
    expect(s.brandColor).toBeNull()
  })
})
