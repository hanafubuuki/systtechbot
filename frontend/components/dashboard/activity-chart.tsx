'use client'

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import { formatDate } from '@/lib/formatters'
import type { TimeSeriesPoint } from '@/types/api'

interface ActivityChartProps {
  data: TimeSeriesPoint[]
  period: number
}

const chartConfig = {
  messages: {
    label: 'Сообщений',
    // Адаптивный цвет: синий в светлой теме, молочный в темной
    color: 'rgb(var(--chart-line))',
  },
} satisfies ChartConfig

export function ActivityChart({ data, period }: ActivityChartProps) {
  // Преобразуем данные для recharts
  const chartData = data.map((point) => ({
    date: formatDate(point.date),
    messages: point.messages,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>График активности</CardTitle>
        <CardDescription>
          Количество сообщений за последние {period} дней
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[400px] w-full">
          <AreaChart
            data={chartData}
            margin={{
              left: 12,
              right: 12,
              top: 12,
              bottom: 12,
            }}
          >
            <CartesianGrid
              vertical={false}
              strokeDasharray="3 3"
              stroke="currentColor"
              opacity={0.1}
            />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
            />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dot" />}
            />
            <defs>
              <linearGradient id="fillMessages" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-messages)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-messages)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <Area
              dataKey="messages"
              type="monotone"
              fill="url(#fillMessages)"
              fillOpacity={0.5}
              stroke="var(--color-messages)"
              strokeWidth={3}
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

