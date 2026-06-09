import { describe, it, expect } from 'vitest'
import { cn, formatDate, timeAgo, formatPhone, formatDuration, capitalize } from './utils'

describe('cn', () => {
  it('combina clases y resuelve conflictos de tailwind', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4')
    expect(cn('text-sm', false && 'hidden', 'font-bold')).toBe('text-sm font-bold')
  })
})

describe('formatDate', () => {
  it('formatea una fecha en español', () => {
    const out = formatDate('2024-01-15T09:30:00')
    expect(out).toContain('enero')
    expect(out).toContain('09:30')
  })

  it('acepta un objeto Date', () => {
    const out = formatDate(new Date('2024-03-01T14:05:00'))
    expect(out).toContain('marzo')
  })
})

describe('timeAgo', () => {
  it('devuelve una distancia relativa con sufijo', () => {
    const past = new Date(Date.now() - 60 * 60 * 1000)
    expect(timeAgo(past)).toMatch(/hace/i)
  })
})

describe('formatPhone', () => {
  it('formatea un número peruano +51', () => {
    expect(formatPhone('+51987654321')).toBe('+51 987 654 321')
  })

  it('deja igual lo que no coincide con el patrón', () => {
    expect(formatPhone('12345')).toBe('12345')
  })
})

describe('formatDuration', () => {
  it('formatea segundos a m:ss', () => {
    expect(formatDuration(0)).toBe('0:00')
    expect(formatDuration(5)).toBe('0:05')
    expect(formatDuration(65)).toBe('1:05')
    expect(formatDuration(600)).toBe('10:00')
  })
})

describe('capitalize', () => {
  it('capitaliza la primera letra', () => {
    expect(capitalize('hola')).toBe('Hola')
    expect(capitalize('A')).toBe('A')
  })
})
