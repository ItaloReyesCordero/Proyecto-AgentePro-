export type PostStatus =
  | 'published'
  | 'scheduled'
  | 'pending_approval'
  | 'draft'
  | 'rejected'

export interface InstagramPost {
  id: string
  caption: string
  image_url: string | null
  status: PostStatus
  scheduled_for: string | null
  published_at: string | null
  created_at: string
  likes_count: number
  comments_count: number
  ai_generated: boolean
  hashtags: string[]
}
