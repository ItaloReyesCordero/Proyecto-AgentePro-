import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { LandingPage } from './pages/landing/LandingPage'
import { LoginPage } from './pages/auth/LoginPage'
import { RegisterPage } from './pages/auth/RegisterPage'
import { ForgotPasswordPage } from './pages/auth/ForgotPasswordPage'
import { DashboardPage } from './pages/dashboard/DashboardPage'
import { ConversationsPage } from './pages/conversations/ConversationsPage'
import { CallsPage } from './pages/calls/CallsPage'
import { AppointmentsPage } from './pages/appointments/AppointmentsPage'
import { ContactsPage } from './pages/contacts/ContactsPage'
import { InstagramPage } from './pages/instagram/InstagramPage'
import { AutomationsPage } from './pages/automations/AutomationsPage'
import { AgentConfigPage } from './pages/agent/AgentConfigPage'
import { SettingsPage } from './pages/settings/SettingsPage'
import { OnboardingPage } from './pages/onboarding/OnboardingPage'
import { UpgradePage } from './pages/upgrade/UpgradePage'
import { AdminPage } from './pages/admin/AdminPage'
import { PrivacyPage } from './pages/legal/PrivacyPage'
import { TermsPage } from './pages/legal/TermsPage'
import { useAuthStore } from './stores/auth.store'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

function SuperAdminRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuthStore()
  if (user?.role !== 'superadmin') return <Navigate to="/app" replace />
  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/privacidad',
    element: <PrivacyPage />,
  },
  {
    path: '/terminos',
    element: <TermsPage />,
  },
  {
    path: '/onboarding',
    element: (
      <ProtectedRoute>
        <OnboardingPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/app/upgrade',
    element: (
      <ProtectedRoute>
        <UpgradePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/app',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'conversations', element: <ConversationsPage /> },
      { path: 'calls', element: <CallsPage /> },
      { path: 'appointments', element: <AppointmentsPage /> },
      { path: 'contacts', element: <ContactsPage /> },
      { path: 'instagram', element: <InstagramPage /> },
      { path: 'automations', element: <AutomationsPage /> },
      { path: 'agent', element: <AgentConfigPage /> },
      { path: 'settings', element: <SettingsPage /> },
      {
        path: 'admin',
        element: (
          <SuperAdminRoute>
            <AdminPage />
          </SuperAdminRoute>
        ),
      },
    ],
  },
])
