/**
 * API client для взаимодействия с backend
 */

import type { StatsResponse, StatsParams, ChatMessage, ChatResponse } from '@/types/api'

/**
 * Получить API URL динамически
 * - Для server-side: используем process.env.API_URL
 * - Для client-side: используем текущий домен с портом 8005
 */
function getApiBaseUrl(): string {
  // Server-side (Next.js SSR/SSG)
  if (typeof window === 'undefined') {
    return process.env.API_URL || 'http://localhost:8000'
  }
  
  // Client-side (браузер)
  // Используем текущий домен/IP, но порт 8005 для API
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  
  // Если localhost - используем стандартный порт 8000
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//localhost:8000`
  }
  
  // Для production - используем текущий IP/домен с портом 8005
  return `${protocol}//${hostname}:8005`
}

const API_BASE_URL = getApiBaseUrl()

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
