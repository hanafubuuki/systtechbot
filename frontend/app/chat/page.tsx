'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Trash2, AlertCircle } from 'lucide-react'
import { ChatHistory } from '@/components/chat/chat-history'
import { ChatInput } from '@/components/chat/chat-input'
import { sendChatMessage, clearChatHistory } from '@/lib/api'
import type { ChatMessage } from '@/types/api'

const USER_ID = 1 // Фиксированный user_id для веб-чата (можно расширить позже)

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSend = async (message: string) => {
    setError(null)

    // Добавляем сообщение пользователя в UI
    const userMessage: ChatMessage = { role: 'user', content: message }
    setMessages((prev) => [...prev, userMessage])

    setIsLoading(true)

    try {
      // Отправляем запрос в API
      const response = await sendChatMessage(USER_ID, message, messages)

      // Добавляем ответ ассистента
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      }
      setMessages((prev) => [...prev, assistantMessage])

      // Логируем SQL если был выполнен (для отладки)
      if (response.sql_executed) {
        console.log('SQL executed:', response.sql_executed)
      }
    } catch (err) {
      console.error('Error sending message:', err)
      setError(
        err instanceof Error
          ? err.message
          : 'Произошла ошибка при отправке сообщения'
      )

      // Удаляем сообщение пользователя из UI при ошибке
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearHistory = async () => {
    if (!confirm('Вы уверены, что хотите очистить историю чата?')) {
      return
    }

    try {
      await clearChatHistory(USER_ID)
      setMessages([])
      setError(null)
    } catch (err) {
      console.error('Error clearing history:', err)
      setError(
        err instanceof Error
          ? err.message
          : 'Произошла ошибка при очистке истории'
      )
    }
  }

  return (
    <div className="container mx-auto flex h-screen max-h-screen flex-col">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Daily Reporter
            </h1>
            <p className="text-sm text-muted-foreground">
              AI-ассистент для помощи с задачами и отчетностью
            </p>
          </div>
          <Button
            onClick={handleClearHistory}
            variant="outline"
            size="sm"
            disabled={messages.length === 0}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Очистить историю
          </Button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mx-4 mt-4 flex items-center gap-2 rounded-md border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
          <Button
            onClick={() => setError(null)}
            variant="ghost"
            size="sm"
            className="ml-auto"
          >
            Закрыть
          </Button>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        <ChatHistory messages={messages} isLoading={isLoading} />
      </div>

      {/* Input area */}
      <Card className="m-4 p-4">
        <ChatInput onSend={handleSend} disabled={isLoading} />
        <div className="mt-2 text-xs text-muted-foreground">
          Нажмите Enter для отправки, Shift+Enter для новой строки
        </div>
      </Card>
    </div>
  )
}
