'use client'

import { useState, useEffect } from 'react'
import { ActivityChart } from './activity-chart'
import { PeriodSelector } from './period-selector'
import { ChartSkeleton } from './chart-skeleton'
import { ErrorMessage } from './error-message'
import { getStats } from '@/lib/api'
import type { TimeSeriesPoint } from '@/types/api'

interface ActivitySectionProps {
  initialData: TimeSeriesPoint[]
  initialPeriod?: number
}

export function ActivitySection({
  initialData,
  initialPeriod = 90,
}: ActivitySectionProps) {
  const [period, setPeriod] = useState(initialPeriod)
  const [data, setData] = useState(initialData)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)

  useEffect(() => {
    // Не загружаем данные при первом рендере (уже есть initialData)
    if (period === initialPeriod) {
      return
    }

    const loadData = async () => {
      setLoading(true)
      setError(false)
      try {
        const stats = await getStats({ period })
        setData(stats.activity_chart)
      } catch (err) {
        console.error('Failed to load activity data:', err)
        setError(true)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [period, initialPeriod])

  const handleRetry = () => {
    setPeriod(initialPeriod)
    setData(initialData)
    setError(false)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Активность</h2>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {error ? (
        <ErrorMessage onRetry={handleRetry} />
      ) : loading ? (
        <ChartSkeleton />
      ) : (
        <ActivityChart data={data} period={period} />
      )}
    </div>
  )
}

