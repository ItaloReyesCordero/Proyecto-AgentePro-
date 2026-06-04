export interface MessageVolumePoint {
  date: string
  count: number
}

export interface LeadsFunnelPoint {
  stage: string
  count: number
}

export interface MetricsSummary {
  total_messages: number
  messages_today: number
  messages_change_pct: number
  new_leads: number
  leads_change_pct: number
  appointments_booked: number
  total_calls: number
  avg_response_time_minutes: number
  hot_leads_count: number
  message_volume_chart: MessageVolumePoint[]
  leads_funnel: LeadsFunnelPoint[]
}
