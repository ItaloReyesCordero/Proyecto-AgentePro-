import { describe, it, expect } from 'vitest'
import { AxiosError } from 'axios'
import { apiErrorMessage } from './api'

function axiosErrorWith(detail: unknown, status = 400): AxiosError {
  return new AxiosError('Request failed', 'ERR', undefined, undefined, {
    data: { detail },
    status,
    statusText: '',
    headers: {},
    config: {} as never,
  })
}

describe('apiErrorMessage', () => {
  it('devuelve el detail cuando es string (HTTPException de FastAPI)', () => {
    const err = axiosErrorWith('Correo o contraseña incorrectos', 401)
    expect(apiErrorMessage(err)).toBe('Correo o contraseña incorrectos')
  })

  it('aplana el array de errores de validación 422', () => {
    const err = axiosErrorWith([{ msg: 'campo requerido' }, { msg: 'email inválido' }], 422)
    expect(apiErrorMessage(err)).toBe('campo requerido · email inválido')
  })

  it('usa el fallback cuando el error no es de axios', () => {
    expect(apiErrorMessage(new Error('x'), 'algo salió mal')).toBe('algo salió mal')
    expect(apiErrorMessage('texto suelto', 'fallback')).toBe('fallback')
  })

  it('cae al message de axios si no hay detail utilizable', () => {
    const err = axiosErrorWith(undefined)
    expect(apiErrorMessage(err)).toBe('Request failed')
  })
})
