import { create } from 'zustand'

export interface Toast {
  id: string
  title: string
  description?: string
  variant: 'default' | 'success' | 'error' | 'warning'
}

interface UIState {
  toasts: Toast[]
  sidebarCollapsed: boolean
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  toggleSidebar: () => void
}

export const useUIStore = create<UIState>((set) => ({
  toasts: [],
  sidebarCollapsed: false,
  addToast: (toast) =>
    set((state) => ({
      toasts: [
        ...state.toasts,
        { ...toast, id: crypto.randomUUID() },
      ],
    })),
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}))

// Helper to use outside React components
export function toast(payload: Omit<Toast, 'id'>) {
  useUIStore.getState().addToast(payload)
}
