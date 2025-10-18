import { Card, CardContent, CardHeader } from '@/components/ui/card'

export function ChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="h-6 w-48 animate-pulse rounded bg-muted" />
      </CardHeader>
      <CardContent>
        <div className="flex h-[400px] items-end justify-between gap-2">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="w-full animate-pulse rounded-t bg-muted"
              style={{
                height: `${Math.random() * 80 + 20}%`,
                animationDelay: `${i * 50}ms`,
              }}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

