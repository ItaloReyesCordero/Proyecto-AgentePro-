import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'

const get = vi.fn()
vi.mock('../../lib/api', () => ({ api: { get: (...a: unknown[]) => get(...a) } }))

import { ActivationCard } from './ActivationCard'
import { renderWithProviders } from '../../test/utils'

function mockEndpoints({ connected, faqs }: { connected: boolean; faqs: number }) {
  get.mockImplementation((url: string) => {
    if (url === '/whatsapp/status') return Promise.resolve({ data: { connected, phone_number_id: null } })
    if (url === '/agent/config') return Promise.resolve({ data: { faqs: Array.from({ length: faqs }, () => ({ question: 'q', answer: 'a' })) } })
    return Promise.resolve({ data: {} })
  })
}

beforeEach(() => get.mockReset())

describe('ActivationCard', () => {
  it('no muestra nada mientras cargan los datos', () => {
    let resolve!: (v: unknown) => void
    get.mockReturnValue(new Promise((r) => { resolve = r }))
    const { container } = renderWithProviders(<ActivationCard />)
    expect(container).toBeEmptyDOMElement()
    resolve({ data: { connected: false } })
  })

  it('no muestra nada cuando WhatsApp está conectado y hay FAQs', async () => {
    mockEndpoints({ connected: true, faqs: 2 })
    const { container } = renderWithProviders(<ActivationCard />)
    await waitFor(() => expect(container).toBeEmptyDOMElement())
  })

  it('muestra la checklist cuando falta configuración', async () => {
    mockEndpoints({ connected: false, faqs: 0 })
    renderWithProviders(<ActivationCard />)
    expect(await screen.findByText(/Termina de activar tu agente/)).toBeInTheDocument()
    expect(screen.getByText('Conecta WhatsApp')).toBeInTheDocument()
    expect(screen.getByText('Configura tu agente')).toBeInTheDocument()
    expect(screen.getByText('WhatsApp desconectado')).toBeInTheDocument()
    // Pasos pendientes con acción
    expect(screen.getAllByText(/Conectar|Configurar|Probar/).length).toBeGreaterThan(0)
  })

  it('refleja WhatsApp conectado pero sin FAQs', async () => {
    mockEndpoints({ connected: true, faqs: 0 })
    renderWithProviders(<ActivationCard />)
    expect(await screen.findByText('WhatsApp conectado')).toBeInTheDocument()
    // El paso de WhatsApp está hecho (texto tachado), el de agente no.
    expect(screen.getByText('Configura tu agente')).toBeInTheDocument()
  })
})
