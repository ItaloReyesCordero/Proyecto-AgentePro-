import type { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { render } from '@testing-library/react'

/** QueryClient sin reintentos ni caché entre tests (deterministico y rápido). */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0, staleTime: 0 },
      mutations: { retry: false },
    },
  })
}

/** Wrapper para hooks que usan react-query. */
export function queryWrapper(client: QueryClient = makeQueryClient()) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>
  }
}

/** Renderiza con react-query + router (para componentes que usan ambos). */
export function renderWithProviders(
  ui: ReactNode,
  { route = '/', client = makeQueryClient() }: { route?: string; client?: QueryClient } = {},
) {
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}
