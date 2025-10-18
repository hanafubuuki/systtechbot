/**
 * TypeScript типы для API responses
 */

// Метрика с трендом
export interface MetricCard {
  value: number
  change_percent: number
  trend: 'up' | 'down' | 'stable'
}

// Точка временного ряда для графика
export interface TimeSeriesPoint {
  date: string // YYYY-MM-DD
  messages: number
}

// Полный ответ от API статистики
export interface StatsResponse {
  total_users: MetricCard
  total_chats: MetricCard
  total_messages: MetricCard
  avg_message_length: MetricCard
  activity_chart: TimeSeriesPoint[]
}

// Параметры запроса статистики
export interface StatsParams {
  period?: number // количество дней (7, 30, 90)
}

// ===== Chat API types =====

// Сообщение в чате
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// Ответ от чата
export interface ChatResponse {
  response: string
  sql_executed?: string
}
