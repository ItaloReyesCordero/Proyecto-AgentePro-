export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export type LeadStage = 'cold' | 'warm' | 'hot' | 'customer' | 'lost'
export type Channel = 'whatsapp' | 'instagram_dm'
export type ConversationStatus =
  | 'open'
  | 'human_takeover'
  | 'closed'
  | 'waiting'
  | 'bot_paused'
export type CallDirection = 'inbound' | 'outbound'
export type CallOutcome =
  | 'appointment_booked'
  | 'info_provided'
  | 'escalated'
  | 'follow_up_needed'
  | 'sale'
  | 'no_interest'
