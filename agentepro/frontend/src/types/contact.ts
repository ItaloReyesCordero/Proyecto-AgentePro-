import type { LeadStage } from './index'

export interface ContactDetail {
  id: string
  wa_id: string | null
  phone: string | null
  name: string | null
  email: string | null
  lead_score: number
  lead_stage: LeadStage
  source: string
  total_interactions: number
  last_interaction_at: string | null
  tags: string[]
  notes: string | null
  created_at: string
}
