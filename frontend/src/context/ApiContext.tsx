import { createContext, useContext, type ReactNode } from 'react'

/**
 * API configuration context.
 *
 * Provides the resolved API base URL to all descendants.
 * The URL is read exclusively from `import.meta.env.VITE_API_BASE_URL`.
 */

interface ApiContextValue {
  /** Resolved base URL (empty string = same origin) */
  baseUrl: string
}

const ApiContext = createContext<ApiContextValue | null>(null)

function resolveBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL ?? ''
  return raw.replace(/\/+$/, '')
}

export function ApiProvider({ children }: { children: ReactNode }) {
  const value: ApiContextValue = { baseUrl: resolveBaseUrl() }
  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>
}

export function useApiConfig(): ApiContextValue {
  const ctx = useContext(ApiContext)
  if (!ctx) {
    throw new Error('useApiConfig must be used within an <ApiProvider>')
  }
  return ctx
}
