import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Message } from '../types/conversation'
import type { PaginatedResponse } from '../types'

export function useMessages(conversationId: string) {
  return useInfiniteQuery({
    queryKey: ['messages', conversationId],
    queryFn: async ({ pageParam = 1 }) => {
      const response = await api.get<PaginatedResponse<Message>>(
        `/conversations/${conversationId}/messages`,
        { params: { page: pageParam, per_page: 50 } },
      )
      return response.data
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.page < lastPage.pages ? lastPage.page + 1 : undefined,
    enabled: !!conversationId,
  })
}

export function useMessagesFlat(conversationId: string) {
  return useQuery({
    queryKey: ['messages', conversationId, 'flat'],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Message>>(
        `/conversations/${conversationId}/messages`,
        { params: { per_page: 100 } },
      )
      return response.data.items
    },
    enabled: !!conversationId,
    refetchInterval: 5000,
  })
}

interface SendMessagePayload {
  conversationId: string
  content: string
  message_type?: 'text'
}

export function useSendMessage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ conversationId, content, message_type = 'text' }: SendMessagePayload) => {
      const response = await api.post<Message>(
        `/conversations/${conversationId}/messages`,
        { content, message_type },
      )
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['messages', variables.conversationId],
      })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}
