import { cn } from '../../lib/utils'

/**
 * Placeholder con efecto "shimmer" para estados de carga. Úsalo en vez de
 * pantallas en blanco mientras TanStack Query trae los datos.
 *
 *   <Skeleton className="h-4 w-32" />
 */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-md bg-text-secondary/10',
        'after:absolute after:inset-0 after:-translate-x-full after:animate-shimmer',
        'after:bg-gradient-to-r after:from-transparent after:via-text-primary/10 after:to-transparent',
        className,
      )}
    />
  )
}

/** Tarjeta-esqueleto lista para grids de KPIs o listas. */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('card-base space-y-3', className)}>
      <Skeleton className="h-9 w-9 rounded-lg" />
      <Skeleton className="h-7 w-20" />
      <Skeleton className="h-3 w-24" />
    </div>
  )
}
