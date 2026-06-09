import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'

const get = vi.fn()
vi.mock('../../lib/api', () => ({ api: { get: (...a: unknown[]) => get(...a) } }))

import { TrialBanner } from './TrialBanner'
import { renderWithProviders } from '../../test/utils'

function inDays(n: number): string {
  return new Date(Date.now() + n * 24 * 60 * 60 * 1000).toISOString()
}

beforeEach(() => get.mockReset())

describe('TrialBanner', () => {
  it('no muestra nada mientras no hay datos', async () => {
    let resolve!: (v: unknown) => void
    get.mockReturnValue(new Promise((r) => { resolve = r }))
    const { container } = renderWithProviders(<TrialBanner />)
    expect(container).toBeEmptyDOMElement()
    resolve({ data: { plan: 'pro', trial_ends_at: null, payment_state: 'ok', payment_due_at: null } })
    await waitFor(() => expect(get).toHaveBeenCalled())
  })

  it('no muestra nada si no hay fecha de vencimiento', async () => {
    get.mockResolvedValue({ data: { plan: 'pro', trial_ends_at: null, payment_state: 'ok', payment_due_at: null } })
    const { container } = renderWithProviders(<TrialBanner />)
    await waitFor(() => expect(get).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it('trial vigente muestra los días restantes', async () => {
    get.mockResolvedValue({ data: { plan: 'trial', trial_ends_at: inDays(10), payment_state: 'ok', payment_due_at: null } })
    renderWithProviders(<TrialBanner />)
    expect(await screen.findByText(/prueba gratuita termina/i)).toBeInTheDocument()
  })

  it('trial con 1 día usa singular "día"', async () => {
    get.mockResolvedValue({ data: { plan: 'trial', trial_ends_at: inDays(0.5), payment_state: 'ok', payment_due_at: null } })
    renderWithProviders(<TrialBanner />)
    expect(await screen.findByText('1', { exact: false })).toBeInTheDocument()
  })

  it('plan pagado al día (no trial) no muestra banner', async () => {
    get.mockResolvedValue({ data: { plan: 'pro', trial_ends_at: null, payment_state: 'ok', payment_due_at: inDays(20) } })
    const { container } = renderWithProviders(<TrialBanner />)
    await waitFor(() => expect(get).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it('estado overdue (trial) muestra mensaje de prueba terminada', async () => {
    get.mockResolvedValue({ data: { plan: 'trial', trial_ends_at: inDays(-1), payment_state: 'overdue', payment_due_at: null } })
    renderWithProviders(<TrialBanner />)
    expect(await screen.findByText(/prueba gratuita terminó/i)).toBeInTheDocument()
  })

  it('estado overdue (pagado) muestra mensualidad vencida', async () => {
    get.mockResolvedValue({ data: { plan: 'pro', trial_ends_at: null, payment_state: 'overdue', payment_due_at: inDays(-1) } })
    renderWithProviders(<TrialBanner />)
    expect(await screen.findByText(/mensualidad venció/i)).toBeInTheDocument()
  })

  it('estado due_soon muestra el aviso de vencimiento próximo', async () => {
    get.mockResolvedValue({ data: { plan: 'pro', trial_ends_at: null, payment_state: 'due_soon', payment_due_at: inDays(2) } })
    renderWithProviders(<TrialBanner />)
    expect(await screen.findByText(/vence en/i)).toBeInTheDocument()
  })

  it('due_soon de trial usa el texto de prueba', async () => {
    get.mockResolvedValue({ data: { plan: 'trial', trial_ends_at: inDays(5), payment_state: 'due_soon', payment_due_at: null } })
    renderWithProviders(<TrialBanner />)
    expect(await screen.findByText(/prueba gratuita/i)).toBeInTheDocument()
  })
})
