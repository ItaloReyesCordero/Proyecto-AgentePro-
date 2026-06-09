import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'

const get = vi.fn()
const post = vi.fn()
const patch = vi.fn()

vi.mock('../lib/api', () => ({
  api: {
    get: (...a: unknown[]) => get(...a),
    post: (...a: unknown[]) => post(...a),
    patch: (...a: unknown[]) => patch(...a),
  },
}))

import { queryWrapper } from '../test/utils'
import { useAutomations, useToggleAutomation, useRunAutomation } from './useAutomations'
import { useCalls, useCall, useStartOutboundCall } from './useCalls'
import { useContacts, useContact, useUpdateContact } from './useContacts'
import {
  useConversations,
  useConversation,
  useTakeoverConversation,
  useReleaseConversation,
  useCloseConversation,
} from './useConversations'
import {
  useInstagramPosts,
  useGeneratePost,
  useApprovePost,
  useRejectPost,
} from './useInstagram'
import { useMessages, useMessagesFlat, useSendMessage } from './useMessages'
import { useMetricsSummary, useMessageVolume, useLeadsFunnel } from './useMetrics'
import { useMyTenant, useHasFeature } from './useTenant'

beforeEach(() => {
  get.mockReset()
  post.mockReset()
  patch.mockReset()
})

describe('useAutomations', () => {
  it('useAutomations consulta /automations', async () => {
    get.mockResolvedValue({ data: [{ id: 'a1' }] })
    const { result } = renderHook(() => useAutomations(), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual([{ id: 'a1' }])
    expect(get).toHaveBeenCalledWith('/automations')
  })

  it('useToggleAutomation hace PATCH', async () => {
    patch.mockResolvedValue({ data: { id: 'a1', is_active: false } })
    const { result } = renderHook(() => useToggleAutomation(), { wrapper: queryWrapper() })
    await act(async () => {
      await result.current.mutateAsync({ id: 'a1', is_active: false })
    })
    expect(patch).toHaveBeenCalledWith('/automations/a1', { is_active: false })
  })

  it('useRunAutomation hace POST run', async () => {
    post.mockResolvedValue({ data: { ok: true } })
    const { result } = renderHook(() => useRunAutomation(), { wrapper: queryWrapper() })
    await act(async () => {
      await result.current.mutateAsync('a1')
    })
    expect(post).toHaveBeenCalledWith('/automations/a1/run')
  })
})

describe('useCalls', () => {
  it('useCalls pasa params', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 1 } })
    const { result } = renderHook(() => useCalls({ status: 'completed' }), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/calls', { params: { status: 'completed' } })
  })

  it('useCall(id) consulta el detalle', async () => {
    get.mockResolvedValue({ data: { id: 'c1' } })
    const { result } = renderHook(() => useCall('c1'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/calls/c1')
  })

  it('useCall("") está deshabilitado', () => {
    const { result } = renderHook(() => useCall(''), { wrapper: queryWrapper() })
    expect(result.current.fetchStatus).toBe('idle')
    expect(get).not.toHaveBeenCalled()
  })

  it('useStartOutboundCall hace POST', async () => {
    post.mockResolvedValue({ data: { id: 'c1' } })
    const { result } = renderHook(() => useStartOutboundCall(), { wrapper: queryWrapper() })
    await act(async () => {
      await result.current.mutateAsync({ to_number: '+51999' })
    })
    expect(post).toHaveBeenCalledWith('/calls/outbound', { to_number: '+51999' })
  })
})

describe('useContacts', () => {
  it('useContacts pasa params', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 1 } })
    const { result } = renderHook(() => useContacts({ search: 'ana' }), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/contacts', { params: { search: 'ana' } })
  })

  it('useContact(id) consulta el detalle', async () => {
    get.mockResolvedValue({ data: { id: 'k1' } })
    const { result } = renderHook(() => useContact('k1'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/contacts/k1')
  })

  it('useContact("") está deshabilitado', () => {
    const { result } = renderHook(() => useContact(''), { wrapper: queryWrapper() })
    expect(result.current.fetchStatus).toBe('idle')
  })

  it('useUpdateContact hace PATCH', async () => {
    patch.mockResolvedValue({ data: { id: 'k1' } })
    const { result } = renderHook(() => useUpdateContact(), { wrapper: queryWrapper() })
    await act(async () => {
      await result.current.mutateAsync({ id: 'k1', data: { name: 'Ana' } })
    })
    expect(patch).toHaveBeenCalledWith('/contacts/k1', { name: 'Ana' })
  })
})

describe('useConversations', () => {
  it('useConversations pasa params', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 1 } })
    const { result } = renderHook(() => useConversations({ status: 'open' }), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/conversations', { params: { status: 'open' } })
  })

  it('useConversation(id)', async () => {
    get.mockResolvedValue({ data: { id: 'v1' } })
    const { result } = renderHook(() => useConversation('v1'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/conversations/v1')
  })

  it('useConversation("") deshabilitado', () => {
    const { result } = renderHook(() => useConversation(''), { wrapper: queryWrapper() })
    expect(result.current.fetchStatus).toBe('idle')
  })

  it('takeover/release/close hacen POST', async () => {
    post.mockResolvedValue({ data: {} })
    const w = queryWrapper()
    const takeover = renderHook(() => useTakeoverConversation(), { wrapper: w })
    await act(async () => { await takeover.result.current.mutateAsync('v1') })
    expect(post).toHaveBeenCalledWith('/conversations/v1/takeover')

    const release = renderHook(() => useReleaseConversation(), { wrapper: w })
    await act(async () => { await release.result.current.mutateAsync('v1') })
    expect(post).toHaveBeenCalledWith('/conversations/v1/release')

    const close = renderHook(() => useCloseConversation(), { wrapper: w })
    await act(async () => { await close.result.current.mutateAsync('v1') })
    expect(post).toHaveBeenCalledWith('/conversations/v1/close')
  })
})

describe('useInstagram', () => {
  it('useInstagramPosts pasa params', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 1 } })
    const { result } = renderHook(() => useInstagramPosts({ status: 'draft' }), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/instagram/posts', { params: { status: 'draft' } })
  })

  it('useGeneratePost hace POST', async () => {
    post.mockResolvedValue({ data: [] })
    const { result } = renderHook(() => useGeneratePost(), { wrapper: queryWrapper() })
    await act(async () => { await result.current.mutateAsync({ week_start: '2024-01-01' }) })
    expect(post).toHaveBeenCalledWith('/instagram/posts/generate', { week_start: '2024-01-01' })
  })

  it('useApprovePost separa id del payload', async () => {
    post.mockResolvedValue({ data: {} })
    const { result } = renderHook(() => useApprovePost(), { wrapper: queryWrapper() })
    await act(async () => { await result.current.mutateAsync({ id: 'p1', caption: 'hola' }) })
    expect(post).toHaveBeenCalledWith('/instagram/posts/p1/approve', { caption: 'hola' })
  })

  it('useRejectPost hace POST', async () => {
    post.mockResolvedValue({ data: {} })
    const { result } = renderHook(() => useRejectPost(), { wrapper: queryWrapper() })
    await act(async () => { await result.current.mutateAsync('p1') })
    expect(post).toHaveBeenCalledWith('/instagram/posts/p1/reject')
  })
})

describe('useMessages', () => {
  it('useMessages (infinite) calcula getNextPageParam', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 2 } })
    const { result } = renderHook(() => useMessages('v1'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.hasNextPage).toBe(true)
    expect(get).toHaveBeenCalledWith('/conversations/v1/messages', { params: { page: 1, per_page: 50 } })
  })

  it('useMessages última página -> sin siguiente', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 1 } })
    const { result } = renderHook(() => useMessages('v1'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.hasNextPage).toBe(false)
  })

  it('useMessages("") deshabilitado', () => {
    const { result } = renderHook(() => useMessages(''), { wrapper: queryWrapper() })
    expect(result.current.fetchStatus).toBe('idle')
  })

  it('useMessagesFlat devuelve items', async () => {
    get.mockResolvedValue({ data: { items: [{ id: 'm1' }], total: 1, page: 1, pages: 1 } })
    const { result } = renderHook(() => useMessagesFlat('v1'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual([{ id: 'm1' }])
  })

  it('useMessagesFlat("") deshabilitado', () => {
    const { result } = renderHook(() => useMessagesFlat(''), { wrapper: queryWrapper() })
    expect(result.current.fetchStatus).toBe('idle')
  })

  it('useSendMessage hace POST con type por defecto', async () => {
    post.mockResolvedValue({ data: { id: 'm2' } })
    const { result } = renderHook(() => useSendMessage(), { wrapper: queryWrapper() })
    await act(async () => {
      await result.current.mutateAsync({ conversationId: 'v1', content: 'hola' })
    })
    expect(post).toHaveBeenCalledWith('/conversations/v1/messages', { content: 'hola', message_type: 'text' })
  })
})

describe('useMetrics', () => {
  it('useMetricsSummary pasa el periodo', async () => {
    get.mockResolvedValue({ data: { total_messages: 0 } })
    const { result } = renderHook(() => useMetricsSummary('30d'), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/metrics/summary', { params: { period: '30d' } })
  })

  it('useMessageVolume usa el periodo por defecto', async () => {
    get.mockResolvedValue({ data: [] })
    const { result } = renderHook(() => useMessageVolume(), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/metrics/message-volume', { params: { period: '7d' } })
  })

  it('useLeadsFunnel consulta el embudo', async () => {
    get.mockResolvedValue({ data: [] })
    const { result } = renderHook(() => useLeadsFunnel(), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/metrics/leads-funnel')
  })
})

describe('useTenant', () => {
  it('useMyTenant consulta /tenants/me', async () => {
    get.mockResolvedValue({ data: { id: 't1', features: ['voice'] } })
    const { result } = renderHook(() => useMyTenant(), { wrapper: queryWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(get).toHaveBeenCalledWith('/tenants/me')
  })

  it('useHasFeature devuelve true/false según features', async () => {
    get.mockResolvedValue({ data: { id: 't1', features: ['voice'] } })
    const w = queryWrapper()
    const { result } = renderHook(
      () => ({ voice: useHasFeature('voice'), insta: useHasFeature('instagram'), tenant: useMyTenant() }),
      { wrapper: w },
    )
    await waitFor(() => expect(result.current.tenant.isSuccess).toBe(true))
    expect(result.current.voice).toBe(true)
    expect(result.current.insta).toBe(false)
  })
})
