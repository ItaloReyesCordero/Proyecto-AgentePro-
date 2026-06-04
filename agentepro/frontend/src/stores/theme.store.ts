import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ThemeMode } from '../lib/theme'

const BRAND_PRESETS = [
  '#10B981', // esmeralda (por defecto)
  '#3B82F6', // azul
  '#8B5CF6', // violeta
  '#EC4899', // rosa
  '#F59E0B', // ámbar
  '#EF4444', // rojo
  '#06B6D4', // cian
  '#0F172A', // pizarra
] as const

const DEFAULT_MODE: ThemeMode = 'dark'

interface UserTheme {
  mode: ThemeMode
  /** Color de marca del cliente (hex). null = usar el verde por defecto. */
  brandColor: string | null
}

interface ThemeState extends UserTheme {
  /** Usuario al que pertenece el tema activo (null = sesión pública / sin login). */
  userId: string | null
  /** Preferencias guardadas POR usuario, para que no se mezclen entre cuentas. */
  byUser: Record<string, UserTheme>
  setMode: (mode: ThemeMode) => void
  toggleMode: () => void
  setBrandColor: (hex: string | null) => void
  /**
   * Carga el tema del usuario indicado (o el por defecto si es null / no tiene
   * preferencias). Llamar al iniciar/cerrar sesión para que el color y el modo
   * sean POR CUENTA y no se hereden entre cuentas en la misma máquina.
   */
  loadForUser: (userId: string | null) => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: DEFAULT_MODE,
      brandColor: null,
      userId: null,
      byUser: {},

      setMode: (mode) => {
        const { userId, byUser, brandColor } = get()
        set({
          mode,
          byUser: userId ? { ...byUser, [userId]: { mode, brandColor } } : byUser,
        })
      },

      toggleMode: () => {
        const next = get().mode === 'dark' ? 'light' : 'dark'
        get().setMode(next)
      },

      setBrandColor: (brandColor) => {
        const { userId, byUser, mode } = get()
        set({
          brandColor,
          byUser: userId ? { ...byUser, [userId]: { mode, brandColor } } : byUser,
        })
      },

      loadForUser: (userId) => {
        if (!userId) {
          // Sesión pública o logout: tema por defecto (no arrastra el de nadie).
          set({ userId: null, mode: DEFAULT_MODE, brandColor: null })
          return
        }
        const saved = get().byUser[userId]
        set({
          userId,
          mode: saved?.mode ?? DEFAULT_MODE,
          brandColor: saved?.brandColor ?? null,
        })
      },
    }),
    {
      name: 'agentepro-theme',
      // Solo persistimos el mapa por usuario; el tema "activo" se reconstruye
      // con loadForUser según quién esté logueado.
      partialize: (s) => ({ byUser: s.byUser }),
    },
  ),
)

export { BRAND_PRESETS }
