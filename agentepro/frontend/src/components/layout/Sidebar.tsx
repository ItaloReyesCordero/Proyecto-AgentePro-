import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  Phone,
  Users,
  Instagram,
  Zap,
  Bot,
  Settings,
  ShieldCheck,
  CalendarCheck,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { cn } from '../../lib/utils'
import { Logo } from '../ui/Logo'
import { useUIStore } from '../../stores/ui.store'
import { useAuthStore } from '../../stores/auth.store'
import { useMyTenant } from '../../hooks/useTenant'

interface NavItem {
  label: string
  path: string
  icon: React.ComponentType<{ className?: string }>
  /** Módulo del plan requerido para ver el ítem. Si no se indica, lo ven todos. */
  feature?: string
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/app', icon: LayoutDashboard },
  { label: 'Conversaciones', path: '/app/conversations', icon: MessageSquare },
  { label: 'Llamadas', path: '/app/calls', icon: Phone, feature: 'voice' },
  { label: 'Citas', path: '/app/appointments', icon: CalendarCheck, feature: 'appointments' },
  { label: 'Contactos', path: '/app/contacts', icon: Users, feature: 'contacts' },
  { label: 'Instagram', path: '/app/instagram', icon: Instagram, feature: 'instagram' },
  { label: 'Automatizaciones', path: '/app/automations', icon: Zap, feature: 'automations' },
  { label: 'Agente IA', path: '/app/agent', icon: Bot },
  { label: 'Configuración', path: '/app/settings', icon: Settings },
]

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore()
  const navigate = useNavigate()
  const role = useAuthStore((s) => s.user?.role)
  const { data: tenant } = useMyTenant()

  // El Super Admin solo administra la plataforma: no ve los módulos de negocio.
  // El dueño solo ve los módulos incluidos en su plan (el resto se oculta).
  const features = tenant?.features ?? []
  const items: NavItem[] =
    role === 'superadmin'
      ? [{ label: 'Super Admin', path: '/app/admin', icon: ShieldCheck }]
      : navItems.filter((it) => !it.feature || features.includes(it.feature))

  return (
    <aside
      className={cn(
        'flex flex-col h-full bg-surface/80 backdrop-blur-xl border-r border-border transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-60',
      )}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-3 px-4 py-5 cursor-pointer select-none"
        onClick={() => navigate('/app')}
      >
        <Logo size={32} showText={!sidebarCollapsed} textClassName="text-lg" />
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-2 space-y-1 overflow-y-auto scrollbar-thin">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/app'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group relative',
                isActive
                  ? 'bg-primary/10 text-primary border-l-2 border-primary pl-[10px]'
                  : 'text-text-secondary hover:bg-text-primary/5 hover:text-text-primary border-l-2 border-transparent',
              )
            }
          >
            <item.icon
              className={cn(
                'w-5 h-5 flex-shrink-0',
                sidebarCollapsed && 'mx-auto',
              )}
            />
            {!sidebarCollapsed && <span>{item.label}</span>}
            {sidebarCollapsed && (
              <div className="absolute left-14 bg-card border border-border text-text-primary text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                {item.label}
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="flex items-center justify-center h-10 border-t border-border text-text-secondary hover:text-text-primary hover:bg-text-primary/5 transition-colors"
        title={sidebarCollapsed ? 'Expandir' : 'Colapsar'}
      >
        {sidebarCollapsed ? (
          <ChevronRight className="w-4 h-4" />
        ) : (
          <ChevronLeft className="w-4 h-4" />
        )}
      </button>
    </aside>
  )
}
