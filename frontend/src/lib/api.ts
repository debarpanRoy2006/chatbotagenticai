/**
 * Centralized API client for the Agentic AI backend.
 */

// ── Types ──
export type ActionType =
  | 'code_generation'
  | 'debugging'
  | 'git_operation'
  | 'analyze_file'
  | 'analyze_image'
  | 'analyze_document'
  | 'generate_ideas'
  | 'general_ai'

export interface AgentRequest {
  action_type: ActionType
  prompt: string
  file?: File
}

export interface AgentResponse {
  result: string
}

export interface HistoryEntry {
  prompt: string
  action_type: string
  file_uploaded?: boolean
  file_type?: string
  result: string
  timestamp: string
}

export interface HistoryResponse {
  history: HistoryEntry[]
}

export interface ApiError {
  error: string
}

// ── Helpers ──
function getBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_BASE_URL ?? ''
  return envUrl.replace(/\/+$/, '')
}

const BASE_URL = getBaseUrl()

// ── API Methods ──

/** POST /api/agent/ — Send a prompt to the agent. */
export async function sendAgentRequest(
  request: AgentRequest,
): Promise<AgentResponse> {
  const formData = new FormData()
  formData.append('action_type', request.action_type)
  formData.append('prompt', request.prompt)

  if (request.file) {
    formData.append('uploaded_file', request.file)
  }

  const response = await fetch(`${BASE_URL}/api/agent/`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorData: ApiError = await response.json().catch(() => ({}))
    throw new Error(errorData.error || `Request failed (${response.status})`)
  }

  return response.json() as Promise<AgentResponse>
}

/** GET /api/history/ — Fetch conversation history. */
export async function fetchHistory(): Promise<HistoryEntry[]> {
  const response = await fetch(`${BASE_URL}/api/history/`)

  if (!response.ok) {
    throw new Error(`Failed to fetch history (${response.status})`)
  }

  const data: HistoryResponse = await response.json()
  return data.history
}

/** DELETE /api/history/clear/ — Clear all conversation history. */
export async function clearHistory(): Promise<void> {
  const response = await fetch(`${BASE_URL}/api/history/clear/`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.error || `Failed to clear history (${response.status})`)
  }
}