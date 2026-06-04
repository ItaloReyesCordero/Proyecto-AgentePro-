import { describe, it, expect } from 'vitest'
import { hexToRgbChannels } from './theme'

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
