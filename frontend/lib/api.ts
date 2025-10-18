/**
 * API client для взаимодействия с backend
 */

import type { StatsResponse, StatsParams, ChatMessage, ChatResponse } from '@/types/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Получить статистику за указанный период
 */
export async function getStats(
  params: StatsParams = {}
): Promise<StatsResponse> {
  const period = params.period || 90
  const url = `${API_BASE_URL}/api/v1/stats?period=${period}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Отправить сообщение в чат
 */
export async function sendChatMessage(
  userId: number,
  message: string,
  history: ChatMessage[] = []
): Promise<ChatResponse> {
  const url = `${API_BASE_URL}/api/v1/chat`

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      message,
      history,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail || `Failed to send message: ${response.statusText}`
    )
  }

  return response.json()
}

/**
 * Очистить историю чата
 */
export async function clearChatHistory(userId: number): Promise<void> {
  const url = `${API_BASE_URL}/api/v1/chat/clear`

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail || `Failed to clear history: ${response.statusText}`
    )
  }
}
