import { useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'
import { cn } from '../../lib/utils'
import { useUIStore, type Toast } from '../../stores/ui.store'

const ICONS = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  default: Info,
}

const COLORS = {
  success: 'border-primary/30 bg-primary/10 text-primary',
  error: 'border-red-500/30 bg-red-500/10 text-red-400',
  warning: 'border-warning/30 bg-warning/10 text-warning',
  default: 'border-secondary/30 bg-secondary/10 text-secondary',
}

function ToastItem({ toast }: { toast: Toast }) {
  const removeToast = useUIStore((s) => s.removeToast)
  const Icon = ICONS[toast.variant]

  useEffect(() => {
    const t = setTimeout(() => removeToast(toast.id), 4500)
    return () => clearTimeout(t)
  }, [toast.id, removeToast])

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 80, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 80, scale: 0.9 }}
      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
      className={cn(
        'relative flex items-start gap-3 overflow-hidden rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md min-w-[280px] max-w-sm',
        COLORS[toast.variant],
      )}
    >
      <Icon className="mt-0.5 h-5 w-5 flex-shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-text-primary">{toast.title}</p>
        {toast.description && (
          <p className="mt-0.5 text-xs text-text-secondary">
            {toast.description}
          </p>
        )}
      </div>
      <button
        onClick={() => removeToast(toast.id)}
        className="flex-shrink-0 text-text-secondary transition-colors hover:text-text-primary"
      >
        <X className="h-4 w-4" />
      </button>
      {/* Barra de progreso que se agota con el auto-cierre */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5 bg-current opacity-40"
        initial={{ width: '100%' }}
        animate={{ width: '0%' }}
        transition={{ duration: 4.5, ease: 'linear' }}
      />
    </motion.div>
  )
}

export function Toaster() {
  const toasts = useUIStore((s) => s.toasts)

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      <AnimatePresence initial={false}>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} />
        ))}
      </AnimatePresence>
    </div>
  )
}
