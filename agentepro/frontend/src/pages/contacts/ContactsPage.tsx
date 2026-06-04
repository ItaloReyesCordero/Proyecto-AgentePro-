import { useState } from 'react'
import { Users, Loader2, Search } from 'lucide-react'
import { useContacts, useUpdateContact } from '../../hooks/useContacts'
import { EmptyState } from '../../components/common/EmptyState'
import type { LeadStage } from '../../types'
import type { Contact } from '../../types/conversation'

const COLUMNS: { stage: LeadStage; label: string; emoji: string }[] = [
  { stage: 'cold', label: 'Frío', emoji: '❄️' },
  { stage: 'warm', label: 'Tibio', emoji: '🌤️' },
  { stage: 'hot', label: 'Caliente', emoji: '🔥' },
  { stage: 'customer', label: 'Cliente', emoji: '⭐' },
]

export function ContactsPage() {
  const { data, isLoading } = useContacts({ per_page: 100 })
  const updateContact = useUpdateContact()
  const [query, setQuery] = useState('')
  const contacts = data?.items ?? []

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
      </div>
    )
  }

  if (contacts.length === 0) {
    return (
      <EmptyState icon={Users} title="Sin contactos" description="Los contactos aparecerán cuando lleguen mensajes." />
    )
  }

  const q = query.trim().toLowerCase()
  const filtered = q
    ? contacts.filter(
        (c) =>
          (c.name ?? '').toLowerCase().includes(q) ||
          (c.phone ?? '').toLowerCase().includes(q),
      )
    : contacts

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar por nombre o teléfono..."
          className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-3 text-sm text-text-primary outline-none focus:border-primary"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
      {COLUMNS.map((col) => {
        const items = filtered.filter((c) => c.lead_stage === col.stage)
        return (
          <div key={col.stage} className="flex flex-col rounded-2xl border border-border bg-card">
            <div className="border-b border-border px-4 py-3">
              <h3 className="font-heading text-sm font-semibold text-text-primary">
                {col.emoji} {col.label}{' '}
                <span className="text-text-secondary">({items.length})</span>
              </h3>
            </div>
            <div className="flex flex-col gap-2 overflow-y-auto scrollbar-thin p-3">
              {items.map((contact) => (
                <ContactCard
                  key={contact.id}
                  contact={contact}
                  onMove={(stage) =>
                    updateContact.mutate({ id: contact.id, data: { lead_stage: stage } })
                  }
                />
              ))}
            </div>
          </div>
        )
      })}
      </div>
    </div>
  )
}

function ContactCard({
  contact,
  onMove,
}: {
  contact: Contact
  onMove: (stage: LeadStage) => void
}) {
  const initials = (contact.name ?? contact.phone ?? '?')
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
  return (
    <div className="rounded-lg border border-border bg-background p-3">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-text-primary">
            {contact.name ?? 'Sin nombre'}
          </p>
          <p className="truncate text-xs text-text-secondary">{contact.phone}</p>
        </div>
        <span className="text-xs font-semibold text-primary">{contact.lead_score}</span>
      </div>
      <select
        value={contact.lead_stage}
        onChange={(e) => onMove(e.target.value as LeadStage)}
        className="mt-2 w-full rounded border border-border bg-card px-2 py-1 text-xs text-text-secondary outline-none"
      >
        {COLUMNS.map((c) => (
          <option key={c.stage} value={c.stage}>
            Mover a {c.label}
          </option>
        ))}
      </select>
    </div>
  )
}
