import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Conversation } from '../types/conversation'
import type { PaginatedResponse } from '../types'

interface ConversationParams {
  status?: string
  channel?: string
  lead_stage?: string
  page?: number
  per_page?: number
}

export function useConversations(params?: ConversationParams) {
  return useQuery({
    queryKey: ['conversations', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Conversation>>(
        '/conversations',
        { params },
      )
      return response.data
    },
  })
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: ['conversations', id],
    queryFn: async () => {
      const response = await api.get<Conversation>(`/conversations/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useTakeoverConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (conversationId: string) =>
      api.post(`/conversations/${conversationId}/takeover`),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['conversations'] }),
  })
}

export function useReleaseConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (conversationId: string) =>
      api.post(`/conversations/${conversationId}/release`),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['conversations'] }),
  })
}

export function useCloseConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (conversationId: string) =>
      api.post(`/conversations/${conversationId}/close`),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['conversations'] }),
  })
}
