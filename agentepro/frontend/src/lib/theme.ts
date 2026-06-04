// Utilidades para aplicar el tema (modo claro/oscuro + color de marca) sobre
// las variables CSS definidas en index.css. Sin dependencias externas.

export type ThemeMode = 'dark' | 'light'

/** Convierte un hex (#RRGGBB / #RGB) a canales "R G B" para las variables CSS. */
export function hexToRgbChannels(hex: string): string | null {
  let h = hex.trim().replace('#', '')
  if (h.length === 3) h = h.split('').map((x) => x + x).join('')
  if (!/^[0-9a-fA-F]{6}$/.test(h)) return null
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  return `${r} ${g} ${b}`
}

/**
 * Aplica el tema al <html>: alterna la clase `light` y, si hay color de marca,
 * sobrescribe la variable --primary. Si brandColor es null/ inválido, restaura
 * el verde por defecto del CSS.
 */
export function applyTheme(mode: ThemeMode, brandColor?: string | null): void {
  const root = document.documentElement
  root.classList.toggle('light', mode === 'light')

  if (brandColor) {
    const channels = hexToRgbChannels(brandColor)
    if (channels) {
      root.style.setProperty('--primary', channels)
      return
    }
  }
  root.style.removeProperty('--primary')
}
