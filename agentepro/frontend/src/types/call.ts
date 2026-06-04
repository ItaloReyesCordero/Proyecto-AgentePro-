import type { CallDirection, CallOutcome } from './index'

export interface CallContact {
  id: string
  name: string | null
  phone: string
}

export interface CallSummary {
  id: string
  key_points: string[]
  action_items: string[]
  sentiment: 'positive' | 'neutral' | 'negative'
  follow_up_required: boolean
  follow_up_date: string | null
  follow_up_notes: string | null
}

export interface Call {
  id: string
  contact: CallContact | null
  direction: CallDirection
  from_number: string
  to_number: string
  status:
    | 'initiated'
    | 'ringing'
    | 'in_progress'
    | 'completed'
    | 'failed'
    | 'no_answer'
    | 'voicemail'
  duration_seconds: number
  recording_url: string | null
  transcript: string | null
  ai_summary: string | null
  intent_detected: string | null
  outcome: CallOutcome | null
  lead_score_before: number
  lead_score_after: number
  started_at: string
  ended_at: string | null
  created_at: string
  summary?: CallSummary
}
