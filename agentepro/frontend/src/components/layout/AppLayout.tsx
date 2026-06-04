import { Outlet, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { TrialBanner } from './TrialBanner'
import { useAuthStore } from '../../stores/auth.store'

export function AppLayout() {
  const role = useAuthStore((s) => s.user?.role)
  const location = useLocation()
  const isSuperAdmin = role === 'superadmin'

  // El Super Admin no tiene negocio propio: solo puede usar el panel de admin.
  // Cualquier otra ruta de /app lo redirige ahí (evita pantallas que cargan vacío).
  if (isSuperAdmin && location.pathname !== '/app/admin') {
    return <Navigate to="/app/admin" replace />
  }

  return (
    <div className="flex h-screen overflow-hidden bg-transparent">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />
        {!isSuperAdmin && <TrialBanner />}
        <main className="scrollbar-thin flex-1 overflow-auto p-6">
          {/* Transición suave entre páginas (keyed por ruta) */}
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
