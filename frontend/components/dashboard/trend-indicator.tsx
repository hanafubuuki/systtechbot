import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatPercent } from '@/lib/formatters'
import type { MetricCard } from '@/types/api'

interface TrendIndicatorProps {
  trend: MetricCard['trend']
  changePercent: number
}

export function TrendIndicator({ trend, changePercent }: TrendIndicatorProps) {
  const Icon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
  const color =
    trend === 'up'
      ? 'text-green-600 dark:text-green-500'
      : trend === 'down'
        ? 'text-red-600 dark:text-red-500'
        : 'text-muted-foreground'

  return (
    <p className={`flex items-center gap-1 text-xs ${color}`}>
      <Icon className="h-4 w-4" />
      <span>{formatPercent(changePercent)}</span>
      <span className="text-muted-foreground">от предыдущего периода</span>
    </p>
  )
}

