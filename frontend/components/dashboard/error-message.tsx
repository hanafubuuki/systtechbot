'use client'

import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ErrorMessageProps {
  onRetry?: () => void
}

export function ErrorMessage({ onRetry }: ErrorMessageProps) {
  return (
    <Card className="border-destructive">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-destructive">
          <AlertCircle className="h-5 w-5" />
          Ошибка загрузки данных
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4 text-sm text-muted-foreground">
          Не удалось загрузить статистику. Проверьте подключение к API и попробуйте снова.
        </p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            Попробовать снова
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

