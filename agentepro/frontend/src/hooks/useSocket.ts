import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { getSocket, disconnectSocket } from '../lib/socket'
import { useAuthStore } from '../stores/auth.store'
import { useUIStore } from '../stores/ui.store'

interface NewMessageEvent {
  conversation_id: string
  message: { id: string; content: string; sender_type: string }
}

interface ConversationUpdatedEvent {
  conversation_id: string
}

export function useSocket() {
  const { token } = useAuthStore()
  const queryClient = useQueryClient()
  const addToast = useUIStore((s) => s.addToast)

  useEffect(() => {
    if (!token) return

    const socket = getSocket()

    socket.on('connect', () => {
      console.log('[Socket] Connected:', socket.id)
    })

    socket.on('disconnect', () => {
      console.log('[Socket] Disconnected')
    })

    socket.on('new_message', (event: NewMessageEvent) => {
      queryClient.invalidateQueries({
        queryKey: ['messages', event.conversation_id],
      })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      // Avisa al dueño cuando un cliente escribe (no cuando responde el bot).
      if (event.message?.sender_type === 'contact') {
        addToast({
          title: 'Nuevo mensaje',
          description: 'Un cliente acaba de escribir por WhatsApp.',
          variant: 'default',
        })
      }
    })

    socket.on('escalation', () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      addToast({
        title: 'Atención requerida',
        description: 'Una conversación necesita intervención humana.',
        variant: 'warning',
      })
    })

    socket.on('conversation_updated', (event: ConversationUpdatedEvent) => {
      queryClient.invalidateQueries({
        queryKey: ['conversations', event.conversation_id],
      })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    })

    socket.on('call_started', () => {
      queryClient.invalidateQueries({ queryKey: ['calls'] })
    })

    socket.on('call_completed', () => {
      queryClient.invalidateQueries({ queryKey: ['calls'] })
      addToast({
        title: 'Llamada completada',
        description: 'La llamada ha finalizado. El resumen estará disponible pronto.',
        variant: 'success',
      })
    })

    socket.on('instagram_post_ready', () => {
      queryClient.invalidateQueries({ queryKey: ['instagram-posts'] })
      addToast({
        title: 'Posts generados',
        description: 'Los nuevos posts de Instagram están listos para revisión.',
        variant: 'default',
      })
    })

    return () => {
      socket.off('connect')
      socket.off('disconnect')
      socket.off('new_message')
      socket.off('escalation')
      socket.off('conversation_updated')
      socket.off('call_started')
      socket.off('call_completed')
      socket.off('instagram_post_ready')
    }
  }, [token, queryClient, addToast])

  useEffect(() => {
    if (!token) {
      disconnectSocket()
    }
  }, [token])
}
