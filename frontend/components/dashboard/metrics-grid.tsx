import { MetricCard } from './metric-card'
import type { StatsResponse } from '@/types/api'

interface MetricsGridProps {
  stats: StatsResponse
}

export function MetricsGrid({ stats }: MetricsGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <MetricCard title="Всего пользователей" metric={stats.total_users} />
      <MetricCard title="Всего диалогов" metric={stats.total_chats} />
      <MetricCard title="Всего сообщений" metric={stats.total_messages} />
      <MetricCard
        title="Средняя длина сообщения"
        metric={stats.avg_message_length}
        isDecimal
      />
    </div>
  )
}

