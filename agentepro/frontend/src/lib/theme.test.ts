import { describe, it, expect, beforeEach } from 'vitest'
import { hexToRgbChannels, applyTheme } from './theme'

describe('hexToRgbChannels', () => {
  it('convierte un hex de 6 dígitos a canales "R G B"', () => {
    expect(hexToRgbChannels('#10B981')).toBe('16 185 129')
    expect(hexToRgbChannels('#000000')).toBe('0 0 0')
    expect(hexToRgbChannels('#FFFFFF')).toBe('255 255 255')
  })

  it('acepta hex sin # y en minúsculas', () => {
    expect(hexToRgbChannels('10b981')).toBe('16 185 129')
  })

  it('expande la forma corta de 3 dígitos', () => {
    expect(hexToRgbChannels('#fff')).toBe('255 255 255')
    expect(hexToRgbChannels('#0a0')).toBe('0 170 0')
  })

  it('devuelve null para entradas inválidas', () => {
    expect(hexToRgbChannels('no-es-color')).toBeNull()
    expect(hexToRgbChannels('#12345')).toBeNull()
    expect(hexToRgbChannels('#GGGGGG')).toBeNull()
    expect(hexToRgbChannels('')).toBeNull()
  })
})

describe('applyTheme', () => {
  beforeEach(() => {
    document.documentElement.className = ''
    document.documentElement.style.removeProperty('--primary')
  })

  it('en modo oscuro quita la clase light y restaura --primary', () => {
    document.documentElement.style.setProperty('--primary', '1 2 3')
    applyTheme('dark')
    expect(document.documentElement.classList.contains('light')).toBe(false)
    expect(document.documentElement.style.getPropertyValue('--primary')).toBe('')
  })

  it('en modo claro agrega la clase light', () => {
    applyTheme('light')
    expect(document.documentElement.classList.contains('light')).toBe(true)
  })

  it('con un brandColor válido sobrescribe --primary', () => {
    applyTheme('dark', '#10B981')
    expect(document.documentElement.style.getPropertyValue('--primary')).toBe('16 185 129')
  })

  it('con un brandColor inválido restaura el color por defecto', () => {
    document.documentElement.style.setProperty('--primary', '9 9 9')
    applyTheme('dark', 'no-es-color')
    expect(document.documentElement.style.getPropertyValue('--primary')).toBe('')
  })

  it('con brandColor null restaura el color por defecto', () => {
    document.documentElement.style.setProperty('--primary', '9 9 9')
    applyTheme('light', null)
    expect(document.documentElement.style.getPropertyValue('--primary')).toBe('')
  })
})
