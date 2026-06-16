import { useState, useCallback } from 'react'
import { sendAgentRequest, type ActionType, type AgentResponse } from '../lib/api'

interface UseAgentReturn {
  // Update signature to return a Promise<boolean>
  sendRequest: (actionType: ActionType, prompt: string, file?: File) => Promise<boolean>
  result: string | null
  isLoading: boolean
  error: string | null
  reset: () => void
}

export function useAgent(): UseAgentReturn {
  const [result, setResult] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])

  const sendRequest = useCallback(
    async (actionType: ActionType, prompt: string, file?: File): Promise<boolean> => {
      setIsLoading(true)
      setError(null)
      setResult(null)

      try {
        const response: AgentResponse = await sendAgentRequest({
          action_type: actionType,
          prompt,
          file,
        })
        setResult(response.result)
        return true // <-- Return true on success
      } catch (err) {
        const message = err instanceof Error ? err.message : 'An unknown error occurred'
        setError(message)
        return false // <-- Return false on error
      } finally {
        setIsLoading(false)
      }
    },
    [],
  )

  return { sendRequest, result, isLoading, error, reset }
}