import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { InstagramPost } from '../types/instagram'
import type { PaginatedResponse } from '../types'

interface PostParams {
  status?: string
  month?: string
  page?: number
}

export function useInstagramPosts(params?: PostParams) {
  return useQuery({
    queryKey: ['instagram-posts', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<InstagramPost>>(
        '/instagram/posts',
        { params },
      )
      return response.data
    },
  })
}

interface GeneratePostsPayload {
  week_start: string
  count?: number
  topics?: string[]
}

export function useGeneratePost() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: GeneratePostsPayload) => {
      const response = await api.post<InstagramPost[]>(
        '/instagram/posts/generate',
        payload,
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instagram-posts'] })
    },
  })
}

interface ApprovePostPayload {
  id: string
  caption?: string
  scheduled_for?: string
}

export function useApprovePost() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...data }: ApprovePostPayload) => {
      const response = await api.post<InstagramPost>(
        `/instagram/posts/${id}/approve`,
        data,
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instagram-posts'] })
    },
  })
}

export function useRejectPost() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<InstagramPost>(
        `/instagram/posts/${id}/reject`,
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instagram-posts'] })
    },
  })
}
