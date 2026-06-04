import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Logo } from '../../components/ui/Logo'

/**
 * Marco común para las páginas legales públicas (Privacidad y Términos).
 * No requiere autenticación: Meta/WhatsApp exige que estas páginas sean
 * accesibles públicamente por URL.
 */
export function LegalLayout({
  title,
  updated,
  children,
}: {
  title: string
  updated: string
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background text-text-primary">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
          <Link to="/">
            <Logo size={32} showText textClassName="text-xl" />
          </Link>
          <Link
            to="/"
            className="flex items-center gap-1.5 text-sm text-text-secondary transition hover:text-text-primary"
          >
            <ArrowLeft className="h-4 w-4" /> Volver al inicio
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="font-heading text-3xl font-bold">{title}</h1>
        <p className="mt-2 text-sm text-text-secondary">Última actualización: {updated}</p>
        <div className="legal-content mt-8 space-y-6 text-sm leading-relaxed text-text-secondary">
          {children}
        </div>
      </main>

      <footer className="border-t border-border py-8 text-center text-sm text-text-secondary">
        <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-center gap-x-4 gap-y-2 px-4">
          <Link to="/privacidad" className="hover:text-text-primary">Política de Privacidad</Link>
          <span className="opacity-40">·</span>
          <Link to="/terminos" className="hover:text-text-primary">Términos y Condiciones</Link>
          <span className="opacity-40">·</span>
          <span>© {new Date().getFullYear()} AgentePro — Italo Eduardo Reyes Cordero · Perú 🇵🇪</span>
        </div>
      </footer>
    </div>
  )
}

/** Título de sección reutilizable dentro del contenido legal. */
export function LegalSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="font-heading text-lg font-semibold text-text-primary">{title}</h2>
      {children}
    </section>
  )
}
