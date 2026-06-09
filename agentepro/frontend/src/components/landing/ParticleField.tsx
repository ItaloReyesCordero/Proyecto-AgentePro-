import { useEffect, useRef } from 'react'
import { cn } from '../../lib/utils'

/**
 * Fondo de partículas tipo "constelación a la deriva": puntos unidos por líneas
 * que fluyen de IZQUIERDA a DERECHA como un río, en los colores de marca
 * (--primary / --secondary). Es un <canvas> ligero, sin dependencias:
 *  - densidad acotada según el área (rendimiento estable),
 *  - se pausa cuando la pestaña no está visible,
 *  - respeta `prefers-reduced-motion` (dibuja un único frame estático).
 */
export function ParticleField({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const dpr = Math.min(window.devicePixelRatio || 1, 2)

    let width = 0
    let height = 0
    let frame = 0
    let rafId = 0

    interface P { x: number; y: number; vx: number; vy: number; r: number; accent: boolean }
    let particles: P[] = []

    // Lee los canales "R G B" de las variables de marca y los pasa a "R,G,B".
    const brandColors = () => {
      const s = getComputedStyle(document.documentElement)
      const p = (s.getPropertyValue('--primary').trim() || '139 92 246').replace(/\s+/g, ',')
      const sec = (s.getPropertyValue('--secondary').trim() || '236 72 153').replace(/\s+/g, ',')
      return { p, sec }
    }
    let colors = brandColors()

    const spawn = (atLeftEdge = false): P => {
      return {
        x: atLeftEdge ? -10 : Math.random() * width,
        y: Math.random() * height,
        vx: 0.18 + Math.random() * 0.4, // río: siempre hacia la derecha
        vy: (Math.random() - 0.5) * 0.12, // leve deriva vertical (orgánico)
        r: 1 + Math.random() * 1.8,
        accent: Math.random() < 0.25, // ~1 de cada 4 en fucsia
      }
    }

    const resize = () => {
      width = canvas.clientWidth
      height = canvas.clientHeight
      canvas.width = Math.floor(width * dpr)
      canvas.height = Math.floor(height * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      const count = Math.max(24, Math.min(90, Math.floor((width * height) / 17000)))
      particles = Array.from({ length: count }, () => spawn())
    }

    const LINK = 132

    const draw = () => {
      ctx.clearRect(0, 0, width, height)

      // Líneas entre puntos cercanos (constelación)
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i]
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j]
          const dx = a.x - b.x
          const dy = a.y - b.y
          const dist = Math.hypot(dx, dy)
          if (dist < LINK) {
            const o = (1 - dist / LINK) * 0.22
            ctx.strokeStyle = `rgba(${colors.p},${o})`
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.stroke()
          }
        }
      }

      // Puntos
      for (const a of particles) {
        ctx.beginPath()
        ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(${a.accent ? colors.sec : colors.p},0.85)`
        ctx.fill()
      }
    }

    const step = () => {
      for (const a of particles) {
        a.x += a.vx
        a.y += a.vy
        // Al salir por la derecha, reaparece por la izquierda (flujo continuo).
        if (a.x > width + 12) {
          a.x = -10
          a.y = Math.random() * height
        }
        if (a.y < -12) a.y = height + 12
        else if (a.y > height + 12) a.y = -12
      }
      draw()
      // Refresca el color de marca de vez en cuando (sigue tema/marca sin coste).
      if ((frame = (frame + 1) % 120) === 0) colors = brandColors()
      rafId = requestAnimationFrame(step)
    }

    resize()
    if (reduce) {
      draw() // un frame estático, sin animación
    } else {
      rafId = requestAnimationFrame(step)
    }

    const onResize = () => resize()
    window.addEventListener('resize', onResize)

    const onVisibility = () => {
      cancelAnimationFrame(rafId)
      if (!reduce && !document.hidden) rafId = requestAnimationFrame(step)
    }
    document.addEventListener('visibilitychange', onVisibility)

    return () => {
      cancelAnimationFrame(rafId)
      window.removeEventListener('resize', onResize)
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      className={cn('pointer-events-none', className)}
    />
  )
}
