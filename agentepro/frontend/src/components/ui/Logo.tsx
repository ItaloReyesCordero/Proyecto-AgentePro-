import { cn } from '../../lib/utils'

interface LogoProps {
  /** Lado del ícono en px (es cuadrado). */
  size?: number
  /** Muestra el wordmark "AgentePro" al lado del ícono. */
  showText?: boolean
  /** Clases extra para el contenedor. */
  className?: string
  /** Clases extra para el texto del wordmark. */
  textClassName?: string
}

/**
 * Marca/ícono de AgentePro: un bot con corona, dibujado como SVG EN LÍNEA.
 * Va embebido en el bundle (no depende de /public), por lo que siempre se ve,
 * incluso en el contenedor de desarrollo de Docker (que no monta /public).
 */
export function LogoMark({ size = 36, className }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      role="img"
      aria-label="AgentePro"
      className={cn('flex-shrink-0', className)}
    >
      <defs>
        <linearGradient id="ap-head" x1="30" y1="40" x2="92" y2="106" gradientUnits="userSpaceOnUse">
          <stop stopColor="#60A5FA" />
          <stop offset="1" stopColor="#2563EB" />
        </linearGradient>
        <linearGradient id="ap-crown" x1="40" y1="8" x2="80" y2="38" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FCD34D" />
          <stop offset="1" stopColor="#F59E0B" />
        </linearGradient>
      </defs>

      {/* Orejas / laterales */}
      <rect x="15" y="62" width="10" height="22" rx="5" fill="#2563EB" />
      <rect x="95" y="62" width="10" height="22" rx="5" fill="#2563EB" />

      {/* Cabeza del bot */}
      <rect x="24" y="40" width="72" height="64" rx="20" fill="url(#ap-head)" />
      <rect x="24" y="40" width="72" height="30" rx="20" fill="#ffffff" opacity="0.10" />

      {/* Ojos */}
      <rect x="40" y="60" width="12" height="22" rx="6" fill="#ffffff" />
      <rect x="68" y="60" width="12" height="22" rx="6" fill="#ffffff" />
      <circle cx="46.5" cy="66" r="2.4" fill="#BFDBFE" />
      <circle cx="74.5" cy="66" r="2.4" fill="#BFDBFE" />

      {/* Sonrisa */}
      <path d="M49 91 Q60 98 71 91" stroke="#ffffff" strokeWidth="3.5" strokeLinecap="round" opacity="0.85" />

      {/* Corona */}
      <path
        d="M38 37 L33 13 L48 26 L60 9 L72 26 L87 13 L82 37 Z"
        fill="url(#ap-crown)"
        stroke="#D97706"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <rect x="38" y="34" width="44" height="7.5" rx="3.5" fill="url(#ap-crown)" stroke="#D97706" strokeWidth="1" />

      {/* Gemas */}
      <circle cx="48" cy="22.5" r="2.6" fill="#34D399" />
      <circle cx="60" cy="18" r="3" fill="#F472B6" />
      <circle cx="72" cy="22.5" r="2.6" fill="#A78BFA" />

      {/* Puntas de la corona */}
      <circle cx="33" cy="13" r="3.1" fill="#FBBF24" stroke="#D97706" strokeWidth="1" />
      <circle cx="60" cy="9" r="3.3" fill="#FBBF24" stroke="#D97706" strokeWidth="1" />
      <circle cx="87" cy="13" r="3.1" fill="#FBBF24" stroke="#D97706" strokeWidth="1" />
    </svg>
  )
}

/**
 * Logo oficial de AgentePro: el ícono (bot con corona) + wordmark opcional.
 * Úsalo en lugar de íconos genéricos para mantener la marca consistente.
 */
export function Logo({ size = 36, showText = false, className, textClassName }: LogoProps) {
  return (
    <span className={cn('inline-flex items-center gap-2.5 select-none', className)}>
      <LogoMark size={size} />
      {showText && (
        <span
          className={cn(
            'font-heading font-bold tracking-tight text-text-primary',
            textClassName,
          )}
        >
          AgentePro
        </span>
      )}
    </span>
  )
}
