import { useState, useEffect, useCallback } from 'react'
import { fetchHistory, clearHistory as clearHistoryApi, type HistoryEntry } from '../lib/api'

interface UseHistoryReturn {
  history: HistoryEntry[]
  isLoading: boolean
  error: string | null
  refetch: () => void
  clear: () => Promise<void>
}

export function useHistory(): UseHistoryReturn {
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await fetchHistory()
      setHistory(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load history'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clear = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      await clearHistoryApi()
      setHistory([]) 
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to clear history'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { history, isLoading, error, refetch: load, clear }
}