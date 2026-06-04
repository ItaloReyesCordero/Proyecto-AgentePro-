export type AutomationTrigger =
  | 'new_lead'
  | 'lead_stage_change'
  | 'no_response_24h'
  | 'appointment_reminder'
  | 'post_call'
  | 'birthday'
  | 'schedule'

export interface AutomationExecution {
  id: string
  executed_at: string
  status: 'success' | 'failed' | 'skipped'
  contact_name: string | null
  notes: string | null
}

export interface Automation {
  id: string
  name: string
  description: string
  trigger: AutomationTrigger
  is_active: boolean
  execution_count: number
  last_executed_at: string | null
  created_at: string
  recent_executions: AutomationExecution[]
}
