/**
 * Компонент для отображения истории сообщений с автопрокруткой
 */

'use client'

import { useEffect, useRef } from 'react'
import { ChatMessage } from './chat-message'
import { Loader2 } from 'lucide-react'
import type { ChatMessage as ChatMessageType } from '@/types/api'

interface ChatHistoryProps {
  messages: ChatMessageType[]
  isLoading?: boolean
}

export function ChatHistory({ messages, isLoading = false }: ChatHistoryProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // Автопрокрутка к последнему сообщению
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex flex-col">
      {messages.length === 0 && !isLoading && (
        <div className="flex h-full items-center justify-center text-center text-muted-foreground">
          <div>
            <p className="mb-2 text-lg font-medium">
              Добро пожаловать в Daily Reporter! 👋
            </p>
            <p className="text-sm">
              Задавайте любые вопросы — я помогу найти ответ.
            </p>
            <div className="mt-4 space-y-2 text-xs">
              <p className="font-medium">Для сотрудников systtech:</p>
              <ul className="list-inside list-disc text-left">
                <li>Над какими задачами я работал сегодня?</li>
                <li>Сколько времени я потратил на задачу X?</li>
                <li>Покажи мою активность за неделю</li>
                <li>Какие сообщения я отправлял вчера?</li>
              </ul>
              <p className="mt-2 text-muted-foreground/70">
                Также можете задавать общие вопросы на любую тему
              </p>
            </div>
          </div>
        </div>
      )}

      {messages.map((msg, index) => (
        <ChatMessage
          key={index}
          role={msg.role}
          content={msg.content}
          timestamp={new Date()}
        />
      ))}

      {isLoading && (
        <div className="mb-4 flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">AI думает...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}

