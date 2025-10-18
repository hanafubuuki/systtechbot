'use client'

import { useEffect, useState } from 'react'
import { getStats } from '@/lib/api'
import { MetricsGrid } from '@/components/dashboard/metrics-grid'
import { ActivitySection } from '@/components/dashboard/activity-section'
import { ErrorMessage } from '@/components/dashboard/error-message'
import type { StatsResponse } from '@/types/api'

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadStats() {
      try {
        setIsLoading(true)
        setError(null)
        const data = await getStats({ period: 90 })
        setStats(data)
      } catch (err) {
        console.error('[Dashboard] Failed to load stats:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setIsLoading(false)
      }
    }

    loadStats()
  }, [])

  if (isLoading) {
    return (
      <div className="container mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Статистика диалогов Telegram-бота systtechbot
          </p>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="text-muted-foreground">Загрузка данных...</div>
        </div>
      </div>
    )
  }

  if (error || !stats) {
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
