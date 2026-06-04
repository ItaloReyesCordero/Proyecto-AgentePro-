import { useLocation, useNavigate } from 'react-router-dom'
import { LogOut, User, ChevronDown, CheckCircle, Sun, Moon } from 'lucide-react'
import { useState } from 'react'
import { cn } from '../../lib/utils'
import { useAuthStore } from '../../stores/auth.store'
import { useThemeStore } from '../../stores/theme.store'

function ThemeToggle() {
  const mode = useThemeStore((s) => s.mode)
  const toggleMode = useThemeStore((s) => s.toggleMode)
  const isDark = mode === 'dark'
  return (
    <button
      onClick={toggleMode}
      title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      aria-label="Cambiar tema"
      className="flex h-8 w-8 items-center justify-center rounded-lg text-text-secondary transition-colors hover:bg-text-primary/5 hover:text-text-primary"
    >
      {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  )
}

const PAGE_TITLES: Record<string, string> = {
  '/app': 'Dashboard',
  '/app/conversations': 'Conversaciones',
  '/app/calls': 'Llamadas',
  '/app/contacts': 'Contactos',
  '/app/instagram': 'Instagram',
  '/app/automations': 'Automatizaciones',
  '/app/agent': 'Agente IA',
  '/app/settings': 'Configuración',
  '/app/admin': 'Super Admin',
}

export function TopBar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'AgentePro'
  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : 'AP'

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="flex items-center justify-between h-14 px-6 border-b border-border bg-surface/80 backdrop-blur-xl flex-shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="font-heading font-semibold text-lg text-text-primary">
          {pageTitle}
        </h1>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/10 border border-primary/20">
          <CheckCircle className="w-3.5 h-3.5 text-primary" />
          <span className="text-xs font-medium text-primary">Sistema activo</span>
        </div>
      </div>

      <div className="flex items-center gap-1">
        <ThemeToggle />
        <div className="relative">
        <button
          onClick={() => setDropdownOpen((o) => !o)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-text-primary/5 transition-colors"
        >
          <div className="w-7 h-7 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-xs font-semibold text-primary">
            {initials}
          </div>
          <span className="text-sm text-text-secondary max-w-[120px] truncate hidden sm:block">
            {user?.full_name ?? 'Usuario'}
          </span>
          <ChevronDown className="w-4 h-4 text-text-secondary" />
        </button>

        {dropdownOpen && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setDropdownOpen(false)}
            />
            <div
              className={cn(
                'absolute right-0 top-full mt-1 w-44 bg-card border border-border rounded-lg shadow-xl z-50 py-1 overflow-hidden',
              )}
            >
              <div className="px-3 py-2 border-b border-border">
                <p className="text-xs text-text-primary font-medium truncate">
                  {user?.full_name}
                </p>
                <p className="text-xs text-text-secondary truncate">
                  {user?.email}
                </p>
              </div>
              {user?.role !== 'superadmin' && (
                <button
                  onClick={() => { setDropdownOpen(false); navigate('/app/settings') }}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-text-primary/5 transition-colors"
                >
                  <User className="w-4 h-4" />
                  Perfil
                </button>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-text-primary/5 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Cerrar sesión
              </button>
            </div>
          </>
        )}
        </div>
      </div>
    </header>
  )
}
