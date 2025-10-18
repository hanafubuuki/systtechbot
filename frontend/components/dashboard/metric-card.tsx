import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendIndicator } from './trend-indicator'
import { formatNumber, formatDecimal } from '@/lib/formatters'
import type { MetricCard as MetricCardType } from '@/types/api'

interface MetricCardProps {
  title: string
  metric: MetricCardType
  isDecimal?: boolean
}

export function MetricCard({ title, metric, isDecimal = false }: MetricCardProps) {
  const formattedValue = isDecimal
    ? formatDecimal(metric.value, 1)
    : formatNumber(Math.round(metric.value))

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formattedValue}</div>
        <TrendIndicator trend={metric.trend} changePercent={metric.change_percent} />
      </CardContent>
    </Card>
  )
}

