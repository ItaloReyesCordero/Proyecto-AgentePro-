import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from './MessageBubble'
import type { Message } from '../../types/conversation'

function msg(overrides: Partial<Message>): Message {
  return {
    id: 'm1',
    conversation_id: 'c1',
    direction: 'inbound',
    message_type: 'text',
    content: 'Hola mundo',
    media_url: null,
    transcription: null,
    sender_type: 'contact',
    is_read: false,
    created_at: new Date(Date.now() - 60_000).toISOString(),
    tokens_used: 0,
    ...overrides,
  }
}

describe('MessageBubble', () => {
  it('mensaje de sistema se centra y muestra contenido', () => {
    render(<MessageBubble message={msg({ sender_type: 'system', content: 'evento' })} />)
    expect(screen.getByText('evento')).toBeInTheDocument()
    expect(screen.queryByText('Contacto')).not.toBeInTheDocument()
  })

  it('mensaje de contacto muestra etiqueta y contenido', () => {
    render(<MessageBubble message={msg({ sender_type: 'contact' })} />)
    expect(screen.getByText('Contacto')).toBeInTheDocument()
    expect(screen.getByText('Hola mundo')).toBeInTheDocument()
  })

  it('mensaje de IA muestra etiqueta IA', () => {
    render(<MessageBubble message={msg({ sender_type: 'ai' })} />)
    expect(screen.getByText('IA')).toBeInTheDocument()
  })

  it('mensaje humano muestra etiqueta Agente', () => {
    render(<MessageBubble message={msg({ sender_type: 'human' })} />)
    expect(screen.getByText('Agente')).toBeInTheDocument()
  })

  it('audio con transcripción muestra el texto transcrito', () => {
    render(
      <MessageBubble
        message={msg({ message_type: 'audio', transcription: 'esto fue dicho' })}
      />,
    )
    expect(screen.getByText('Audio transcrito')).toBeInTheDocument()
    expect(screen.getByText('esto fue dicho')).toBeInTheDocument()
  })

  it('audio sin transcripción cae al contenido normal', () => {
    render(
      <MessageBubble message={msg({ message_type: 'audio', transcription: null, content: 'fallback' })} />,
    )
    expect(screen.queryByText('Audio transcrito')).not.toBeInTheDocument()
    expect(screen.getByText('fallback')).toBeInTheDocument()
  })
})
