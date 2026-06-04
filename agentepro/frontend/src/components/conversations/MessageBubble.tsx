import { cn, timeAgo } from '../../lib/utils'
import type { Message } from '../../types/conversation'

interface MessageBubbleProps {
  message: Message
}

const SENDER_CONFIG = {
  contact: {
    align: 'left' as const,
    bubble: 'bg-[#1F2937] text-text-primary rounded-tl-sm',
    label: 'Contacto',
    labelColor: 'text-text-secondary',
  },
  ai: {
    align: 'right' as const,
    bubble: 'bg-primary/15 text-text-primary border border-primary/20 rounded-tr-sm',
    label: 'IA',
    labelColor: 'text-primary',
  },
  human: {
    align: 'right' as const,
    bubble: 'bg-secondary/15 text-text-primary border border-secondary/20 rounded-tr-sm',
    label: 'Agente',
    labelColor: 'text-secondary',
  },
  system: {
    align: 'center' as const,
    bubble: 'bg-text-primary/5 text-text-secondary text-xs rounded-full px-4',
    label: '',
    labelColor: '',
  },
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const config = SENDER_CONFIG[message.sender_type]

  if (config.align === 'center') {
    return (
      <div className="flex justify-center my-2">
        <span className={cn('py-1', config.bubble)}>{message.content}</span>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'flex flex-col gap-0.5 max-w-[75%]',
        config.align === 'right' ? 'ml-auto items-end' : 'items-start',
      )}
    >
      <span className={cn('text-xs font-medium px-1', config.labelColor)}>
        {config.label}
      </span>
      <div
        className={cn(
          'px-4 py-2.5 rounded-2xl text-sm leading-relaxed',
          config.bubble,
        )}
      >
        {message.message_type === 'audio' && message.transcription ? (
          <div>
            <div className="flex items-center gap-2 mb-1 text-text-secondary text-xs">
              <span>Audio transcrito</span>
            </div>
            <p>{message.transcription}</p>
          </div>
        ) : (
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        )}
      </div>
      <span className="text-[11px] text-text-secondary px-1">
        {timeAgo(message.created_at)}
      </span>
    </div>
  )
}
