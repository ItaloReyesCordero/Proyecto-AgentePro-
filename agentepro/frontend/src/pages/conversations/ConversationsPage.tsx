import { useState } from 'react'
import { MessageSquare, Send, UserCheck, Bot, Loader2 } from 'lucide-react'
import { useConversations, useTakeoverConversation, useReleaseConversation } from '../../hooks/useConversations'
import { useMessagesFlat, useSendMessage } from '../../hooks/useMessages'
import { MessageBubble } from '../../components/conversations/MessageBubble'
import { StatusBadge } from '../../components/common/StatusBadge'
import { EmptyState } from '../../components/common/EmptyState'
import { cn, timeAgo } from '../../lib/utils'

export function ConversationsPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const { data, isLoading } = useConversations()
  const conversations = data?.items ?? []
  const selected = conversations.find((c) => c.id === selectedId) ?? null

  return (
    <div className="flex h-[calc(100vh-7rem)] overflow-hidden rounded-2xl border border-border bg-card">
      {/* Lista */}
      <div className="flex w-80 flex-col border-r border-border">
        <div className="border-b border-border px-4 py-3">
          <h3 className="font-heading font-semibold text-text-primary">Conversaciones</h3>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="h-5 w-5 animate-spin text-text-secondary" />
            </div>
          ) : conversations.length === 0 ? (
            <EmptyState icon={MessageSquare} title="Sin conversaciones" description="Aún no hay chats." />
          ) : (
            conversations.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedId(c.id)}
                className={cn(
                  'flex w-full flex-col gap-1 border-b border-border/50 px-4 py-3 text-left transition hover:bg-text-primary/5',
                  selectedId === c.id && 'bg-text-primary/5',
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate text-sm font-medium text-text-primary">
                    {c.contact?.name ?? c.contact?.phone ?? 'Contacto'}
                  </span>
                  <span className="text-[10px] text-text-secondary">
                    {c.last_message_at ? timeAgo(c.last_message_at) : ''}
                  </span>
                </div>
                <p className="truncate text-xs text-text-secondary">
                  {c.last_message?.content ?? 'Sin mensajes'}
                </p>
                <div className="flex items-center gap-1.5">
                  <StatusBadge status={c.status} />
                  <StatusBadge status={c.lead_stage} />
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Thread */}
      <div className="flex flex-1 flex-col">
        {selected ? (
          <Thread
            conversationId={selected.id}
            contactName={selected.contact?.name ?? selected.contact?.phone ?? 'Contacto'}
            assignedToHuman={selected.assigned_to_human}
          />
        ) : (
          <EmptyState
            icon={MessageSquare}
            title="Selecciona una conversación"
            description="Elige un chat de la izquierda para ver los mensajes."
            className="m-auto"
          />
        )}
      </div>
    </div>
  )
}

function Thread({
  conversationId,
  contactName,
  assignedToHuman,
}: {
  conversationId: string
  contactName: string
  assignedToHuman: boolean
}) {
  const { data: messages } = useMessagesFlat(conversationId)
  const takeover = useTakeoverConversation()
  const release = useReleaseConversation()
  const sendMessage = useSendMessage()
  const [draft, setDraft] = useState('')

  function handleSend(e: React.FormEvent) {
    e.preventDefault()
    if (!draft.trim()) return
    sendMessage.mutate({ conversationId, content: draft })
    setDraft('')
  }

  return (
    <>
      <div className="flex items-center justify-between border-b border-border px-5 py-3">
        <div>
          <p className="font-medium text-text-primary">{contactName}</p>
          <p className="text-xs text-text-secondary">
            {assignedToHuman ? 'Atendido por un humano' : 'Atendido por IA'}
          </p>
        </div>
        {assignedToHuman ? (
          <button
            onClick={() => release.mutate(conversationId)}
            className="flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary/90"
          >
            <Bot className="h-4 w-4" /> Devolver a IA
          </button>
        ) : (
          <button
            onClick={() => takeover.mutate(conversationId)}
            className="flex items-center gap-2 rounded-lg bg-red-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-600"
          >
            <UserCheck className="h-4 w-4" /> Tomar control
          </button>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-3 overflow-y-auto scrollbar-thin p-5">
        {(messages ?? []).map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
      </div>

      <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-border p-3">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Escribe un mensaje..."
          className="input-base flex-1"
        />
        <button type="submit" className="btn-primary" disabled={sendMessage.isPending}>
          <Send className="h-4 w-4" />
        </button>
      </form>
    </>
  )
}
