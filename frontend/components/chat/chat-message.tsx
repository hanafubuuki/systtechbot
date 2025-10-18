/**
 * Компонент для отображения одного сообщения в чате
 */

import { cn } from '@/lib/utils'

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={cn(
        'mb-4 flex w-full',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-3',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
        )}
      >
        <div className="mb-1 flex items-center gap-2">
          <span className="text-xs font-semibold">
            {isUser ? 'Вы' : 'AI Ассистент'}
          </span>
          {timestamp && (
            <span className="text-xs opacity-70">
              {timestamp.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          )}
        </div>
        <div className="whitespace-pre-wrap break-words text-sm">
          {content}
        </div>
      </div>
    </div>
  )
}

