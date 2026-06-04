import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Call } from '../types/call'
import type { PaginatedResponse } from '../types'

interface CallParams {
  direction?: string
  status?: string
  outcome?: string
  page?: number
  per_page?: number
}

export function useCalls(params?: CallParams) {
  return useQuery({
    queryKey: ['calls', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Call>>('/calls', {
        params,
      })
      return response.data
    },
  })
}

export function useCall(id: string) {
  return useQuery({
    queryKey: ['calls', id],
    queryFn: async () => {
      const response = await api.get<Call>(`/calls/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

interface OutboundCallPayload {
  to_number: string
  contact_id?: string
}

export function useStartOutboundCall() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: OutboundCallPayload) => {
      const response = await api.post<Call>('/calls/outbound', payload)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calls'] })
    },
  })
}
