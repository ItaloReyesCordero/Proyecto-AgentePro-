import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Automation } from '../types/automation'

export function useAutomations() {
  return useQuery({
    queryKey: ['automations'],
    queryFn: async () => {
      const response = await api.get<Automation[]>('/automations')
      return response.data
    },
  })
}

export function useToggleAutomation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      is_active,
    }: {
      id: string
      is_active: boolean
    }) => {
      const response = await api.patch<Automation>(`/automations/${id}`, {
        is_active,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] })
    },
  })
}

export function useRunAutomation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post(`/automations/${id}/run`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] })
    },
  })
}
