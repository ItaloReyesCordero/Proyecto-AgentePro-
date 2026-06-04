import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Contact } from '../types/conversation'
import type { PaginatedResponse, LeadStage } from '../types'

interface ContactParams {
  lead_stage?: LeadStage
  search?: string
  page?: number
  per_page?: number
}

export function useContacts(params?: ContactParams) {
  return useQuery({
    queryKey: ['contacts', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Contact>>('/contacts', {
        params,
      })
      return response.data
    },
  })
}

export function useContact(id: string) {
  return useQuery({
    queryKey: ['contacts', id],
    queryFn: async () => {
      const response = await api.get<Contact>(`/contacts/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

interface UpdateContactPayload {
  id: string
  data: Partial<Pick<Contact, 'name' | 'email' | 'tags' | 'lead_stage'>>
}

export function useUpdateContact() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: UpdateContactPayload) => {
      const response = await api.patch<Contact>(`/contacts/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
    },
  })
}
