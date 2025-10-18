import { getStats } from '@/lib/api'
import { MetricsGrid } from '@/components/dashboard/metrics-grid'
import { ActivitySection } from '@/components/dashboard/activity-section'
import { ErrorMessage } from '@/components/dashboard/error-message'

export default async function DashboardPage() {
  let stats

  try {
    // Server Component загрузка данных с period=90 по умолчанию
    stats = await getStats({ period: 90 })
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
    return (
      <div className="container mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Статистика диалогов Telegram-бота systtechbot
          </p>
        </div>
        <ErrorMessage />
      </div>
    )
  }

  return (
    <div className="container mx-auto space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Статистика диалогов Telegram-бота systtechbot
        </p>
      </div>

      <MetricsGrid stats={stats} />

      <ActivitySection initialData={stats.activity_chart} initialPeriod={90} />
    </div>
  )
}
