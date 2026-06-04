import { motion, useReducedMotion } from 'framer-motion'

/**
 * Fondo premium animado: auroras/blobs de color desenfocados que se mueven
 * lentamente, más una sutil malla de puntos. Se monta una sola vez (global) y
 * vive DETRÁS de todo (fixed, z -10, sin capturar clics). Usa el color de marca
 * (var --primary) y el secundario, así que cambia con el tema del cliente.
 *
 * Respeta "prefers-reduced-motion": si el usuario lo pide, queda estático.
 */
export function AnimatedBackground() {
  const reduce = useReducedMotion()

  // Cada aurora: posición, tamaño, color (variable CSS) y recorrido de animación.
  const blobs = [
    {
      className: 'left-[-10%] top-[-10%] h-[42vw] w-[42vw] bg-primary/30',
      anim: { x: [0, 60, -20, 0], y: [0, 40, 80, 0], scale: [1, 1.15, 0.95, 1] },
      duration: 26,
    },
    {
      className: 'right-[-12%] top-[8%] h-[38vw] w-[38vw] bg-secondary/25',
      anim: { x: [0, -50, 30, 0], y: [0, 60, -30, 0], scale: [1, 0.9, 1.1, 1] },
      duration: 32,
    },
    {
      className: 'bottom-[-15%] left-[20%] h-[40vw] w-[40vw] bg-primary/20',
      anim: { x: [0, 40, -60, 0], y: [0, -40, 20, 0], scale: [1, 1.1, 0.9, 1] },
      duration: 38,
    },
  ]

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-background"
    >
      {blobs.map((b, i) => (
        <motion.div
          key={i}
          className={`absolute rounded-full blur-[90px] ${b.className}`}
          animate={reduce ? undefined : b.anim}
          transition={{
            duration: b.duration,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Malla de puntos muy sutil para textura */}
      <div
        className="absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage:
            'radial-gradient(currentColor 1px, transparent 1px)',
          backgroundSize: '28px 28px',
          color: 'rgb(var(--text-primary))',
        }}
      />

      {/* Viñeta suave para que el contenido respire */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/60" />
    </div>
  )
}
