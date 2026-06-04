import { useEffect } from 'react'
import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import { Toaster } from './components/ui/Toaster'
import { AnimatedBackground } from './components/common/AnimatedBackground'
import { useSocket } from './hooks/useSocket'
import { useThemeStore } from './stores/theme.store'
import { useAuthStore } from './stores/auth.store'
import { applyTheme } from './lib/theme'

function App() {
  useSocket()
  const mode = useThemeStore((s) => s.mode)
  const brandColor = useThemeStore((s) => s.brandColor)
  const loadForUser = useThemeStore((s) => s.loadForUser)
  const userId = useAuthStore((s) => s.user?.id ?? null)

  // El tema es POR CUENTA: al iniciar/cambiar/cerrar sesión cargamos las
  // preferencias del usuario activo (o las por defecto). Así el color de un
  // negocio no se "pega" a la cuenta de super admin ni a otra cuenta.
  useEffect(() => {
    loadForUser(userId)
  }, [userId, loadForUser])

  // Aplica el tema (modo + color de marca) al <html> y reacciona a los cambios.
  useEffect(() => {
    applyTheme(mode, brandColor)
  }, [mode, brandColor])

  return (
    <>
      <AnimatedBackground />
      <RouterProvider router={router} />
      <Toaster />
    </>
  )
}

export default App
