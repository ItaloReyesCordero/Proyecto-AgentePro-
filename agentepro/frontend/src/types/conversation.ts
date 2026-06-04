import type { LeadStage, Channel, ConversationStatus } from './index'

export interface Contact {
  id: string
  wa_id: string
  phone: string
  name: string | null
  email: string | null
  lead_score: number
  lead_stage: LeadStage
  source: string
  total_interactions: number
  last_interaction_at: string
  tags: string[]
  created_at: string
}

export interface Message {
  id: string
  conversation_id: string
  direction: 'inbound' | 'outbound'
  message_type:
    | 'text'
    | 'audio'
    | 'image'
    | 'document'
    | 'template'
    | 'system'
  content: string
  media_url: string | null
  transcription: string | null
  sender_type: 'contact' | 'ai' | 'human' | 'system'
  is_read: boolean
  created_at: string
  tokens_used: number
}

export interface Conversation {
  id: string
  contact: Contact
  channel: Channel
  status: ConversationStatus
  assigned_to_human: boolean
  lead_score: number
  lead_stage: LeadStage
  last_message_at: string
  tags: string[]
  unread_count?: number
  last_message?: Message
}
