import { type LucideIcon } from 'lucide-react'
import { motion, useReducedMotion } from 'framer-motion'
import { cn } from '../../lib/utils'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const reduce = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'flex flex-col items-center justify-center px-6 py-16 text-center',
        className,
      )}
    >
      <div className="relative mb-5">
        {/* Halo de marca difuminado detrás del ícono */}
        <div className="absolute inset-0 -z-10 rounded-full bg-primary/20 blur-2xl" />
        <motion.div
          animate={reduce ? undefined : { y: [0, -6, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
          className="flex h-16 w-16 items-center justify-center rounded-2xl border border-border bg-gradient-to-br from-primary/15 to-secondary/10"
        >
          <Icon className="h-7 w-7 text-primary" />
        </motion.div>
      </div>
      <h3 className="mb-1 font-heading text-base font-semibold text-text-primary">
        {title}
      </h3>
      {description && (
        <p className="max-w-xs text-sm text-text-secondary">{description}</p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </motion.div>
  )
}
