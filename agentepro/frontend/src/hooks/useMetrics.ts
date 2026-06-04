import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { MetricsSummary, MessageVolumePoint, LeadsFunnelPoint } from '../types/metrics'

type Period = '7d' | '30d' | '90d'

export function useMetricsSummary(period: Period = '7d') {
  return useQuery({
    queryKey: ['metrics', 'summary', period],
    queryFn: async () => {
      const response = await api.get<MetricsSummary>('/metrics/summary', {
        params: { period },
      })
      return response.data
    },
    refetchInterval: 60_000,
  })
}

export function useMessageVolume(period: Period = '7d') {
  return useQuery({
    queryKey: ['metrics', 'message-volume', period],
    queryFn: async () => {
      const response = await api.get<MessageVolumePoint[]>(
        '/metrics/message-volume',
        { params: { period } },
      )
      return response.data
    },
  })
}

export function useLeadsFunnel() {
  return useQuery({
    queryKey: ['metrics', 'leads-funnel'],
    queryFn: async () => {
      const response = await api.get<LeadsFunnelPoint[]>(
        '/metrics/leads-funnel',
      )
      return response.data
    },
  })
}
