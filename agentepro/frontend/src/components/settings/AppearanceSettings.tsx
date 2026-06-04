import { Palette, Sun, Moon, Check, RotateCcw } from 'lucide-react'
import { cn } from '../../lib/utils'
import { useThemeStore, BRAND_PRESETS } from '../../stores/theme.store'
import { toast } from '../../stores/ui.store'

/**
 * Apariencia: modo claro/oscuro y color de marca del negocio. Los cambios se
 * aplican al instante (App.tsx reacciona al store) y se guardan en localStorage.
 */
export function AppearanceSettings() {
  const { mode, setMode, brandColor, setBrandColor } = useThemeStore()
  const current = brandColor ?? '#10B981'

  return (
    <section className="card-base space-y-4">
      <div className="flex items-center gap-2">
        <Palette className="h-5 w-5 text-primary" />
        <h3 className="font-heading font-semibold text-text-primary">Apariencia</h3>
      </div>

      {/* Modo claro / oscuro */}
      <div>
        <p className="mb-2 text-sm font-medium text-text-secondary">Tema</p>
        <div className="grid grid-cols-2 gap-3">
          {(['dark', 'light'] as const).map((m) => {
            const active = mode === m
            const Icon = m === 'dark' ? Moon : Sun
            return (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={cn(
                  'flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-medium transition',
                  active
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border text-text-secondary hover:border-text-secondary/40',
                )}
              >
                <Icon className="h-4 w-4" />
                {m === 'dark' ? 'Oscuro' : 'Claro'}
                {active && <Check className="h-3.5 w-3.5" />}
              </button>
            )
          })}
        </div>
      </div>

      {/* Color de marca */}
      <div>
        <p className="mb-2 text-sm font-medium text-text-secondary">Color de marca</p>
        <div className="flex flex-wrap items-center gap-2">
          {BRAND_PRESETS.map((hex) => {
            const active = current.toLowerCase() === hex.toLowerCase()
            return (
              <button
                key={hex}
                onClick={() => setBrandColor(hex)}
                title={hex}
                style={{ backgroundColor: hex }}
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full ring-2 ring-offset-2 ring-offset-card transition',
                  active ? 'ring-text-primary' : 'ring-transparent hover:ring-border',
                )}
              >
                {active && <Check className="h-4 w-4 text-white" />}
              </button>
            )
          })}

          {/* Selector de color personalizado */}
          <label
            className="flex h-8 cursor-pointer items-center gap-2 rounded-full border border-border px-3 text-xs text-text-secondary hover:border-text-secondary/40"
            title="Color personalizado"
          >
            <span
              className="h-4 w-4 rounded-full border border-border"
              style={{ backgroundColor: current }}
            />
            Personalizado
            <input
              type="color"
              value={current}
              onChange={(e) => setBrandColor(e.target.value)}
              className="sr-only"
            />
          </label>

          {brandColor && (
            <button
              onClick={() => {
                setBrandColor(null)
                toast({ variant: 'default', title: 'Color restablecido' })
              }}
              className="flex h-8 items-center gap-1.5 rounded-full px-3 text-xs text-text-secondary transition hover:text-text-primary"
              title="Volver al color por defecto"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Restablecer
            </button>
          )}
        </div>
        <p className="mt-2 text-xs text-text-secondary">
          Personaliza el color principal de tu panel. Se aplica al instante.
        </p>
      </div>
    </section>
  )
}
