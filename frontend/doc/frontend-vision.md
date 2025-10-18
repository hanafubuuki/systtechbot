# Техническое видение Frontend

**Дата:** 2025-10-17
**Версия:** 1.0
**Спринт:** S2 - Инициализация Frontend проекта

---

## Обзор

Данный документ описывает техническое видение и архитектурные принципы frontend части проекта systtechbot.

## Архитектурный подход

### Next.js App Router

Используем современный подход Next.js 15 с App Router:

- **React Server Components (RSC)** по умолчанию
- **Client Components** (`'use client'`) только когда необходимо:
  - Интерактивность (onClick, onChange)
  - React hooks (useState, useEffect)
  - Browser APIs (window, localStorage)
  - Context providers

**Преимущества RSC:**

- Меньше JavaScript на клиенте
- Быстрая загрузка страниц
- Прямой доступ к backend (в Server Components)
- Automatic code splitting

### Файловая маршрутизация

```
app/
├── layout.tsx              # Root layout (общий для всех страниц)
├── page.tsx               # Главная страница (/)
├── dashboard/
│   └── page.tsx          # Дашборд (/dashboard)
└── chat/
    └── page.tsx          # Чат (/chat)
```

**Conventions:**

- `page.tsx` - публичная страница
- `layout.tsx` - общий layout для вложенных страниц
- `loading.tsx` - UI состояния загрузки (Suspense)
- `error.tsx` - обработка ошибок
- `not-found.tsx` - 404 страница

## Принципы разработки

### 1. KISS (Keep It Simple, Stupid)

- Простота важнее умности
- Избегаем преждевременной оптимизации
- Понятный код важнее краткого

**Пример:**

```typescript
// ✅ Хорошо: простой и понятный
const userCount = users.length

// ❌ Плохо: умно, но непонятно
const userCount = users.reduce((acc) => acc + 1, 0)
```

### 2. DRY (Don't Repeat Yourself)

- Извлекаем повторяющуюся логику в функции/компоненты
- Используем композицию для переиспользования
- Shared типы для frontend и backend (опционально)

### 3. Композиция над наследованием

React components строятся через композицию:

```typescript
// ✅ Хорошо: композиция
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// ❌ Плохо: наследование
class MyCard extends Card { ... }
```

### 4. Separation of Concerns

- **Presentation Components**: UI рендеринг без логики
- **Container Components**: Логика и state management
- **Hooks**: Переиспользуемая логика
- **Utils**: Чистые функции

## Паттерны компонентов

### Server Component (по умолчанию)

```typescript
// app/dashboard/page.tsx
import { getStats } from '@/lib/api'
import { StatsCard } from '@/components/dashboard/stats-card'

export default async function DashboardPage() {
  // Fetching на сервере
  const stats = await getStats({ period: 90 })

  return (
    <div>
      <StatsCard data={stats} />
    </div>
  )
}
```

**Когда использовать:**

- Статический контент
- Data fetching
- SEO-важные страницы

### Client Component

```typescript
'use client'

import { useState } from 'react'

export function PeriodSelector() {
  const [period, setPeriod] = useState(90)

  return (
    <select value={period} onChange={(e) => setPeriod(Number(e.target.value))}>
      <option value={7}>7 дней</option>
      <option value={30}>30 дней</option>
      <option value={90}>90 дней</option>
    </select>
  )
}
```

**Когда использовать:**

- Интерактивные элементы
- State management
- Browser APIs

### Presentation Component

```typescript
// components/dashboard/stats-card.tsx
interface StatsCardProps {
  title: string
  value: number
  trend: 'up' | 'down' | 'stable'
}

export function StatsCard({ title, value, trend }: StatsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <TrendIndicator trend={trend} />
      </CardContent>
    </Card>
  )
}
```

**Характеристики:**

- Нет state
- Только props
- Чистый UI рендеринг
- Легко тестировать

## Управление состоянием

### Local State (useState)

Для простого UI state:

```typescript
const [isOpen, setIsOpen] = useState(false)
const [period, setPeriod] = useState(90)
```

### Server State

Данные с backend - Server Components или React Query (планируется):

```typescript
// Server Component
const stats = await getStats({ period: 90 })

// Client Component (в будущем)
const { data, isLoading } = useQuery('stats', () => getStats({ period: 90 }))
```

### URL State

Для состояния, связанного с навигацией:

```typescript
// app/dashboard/page.tsx
export default function DashboardPage({
  searchParams,
}: {
  searchParams: { period?: string }
}) {
  const period = Number(searchParams.period) || 90
  // ...
}
```

**В будущем (при необходимости):**

- Zustand для глобального state
- Jotai для атомарного state
- Context API для темизации

## Стратегия типизации

### Строгая типизация

```typescript
// ✅ Хорошо: явные типы для API
export async function getStats(params: StatsParams): Promise<StatsResponse> {
  // ...
}

// ✅ Хорошо: типы для props
interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary'
}
```

### Shared типы

```typescript
// types/api.ts
export interface MetricCard {
  value: number
  change_percent: number
  trend: 'up' | 'down' | 'stable'
}

// Используется и в компонентах, и в API клиенте
```

### Type inference

```typescript
// ✅ Хорошо: выводимые типы для простых случаев
const users = await getUsers() // тип выводится из getUsers()
const count = users.length // тип number выводится автоматически
```

## Подход к стилизации

### Tailwind CSS utility-first

```typescript
<div className="flex items-center gap-4 p-6 rounded-lg bg-slate-100">
  <h1 className="text-2xl font-bold">Title</h1>
</div>
```

**Преимущества:**

- Быстрая разработка
- Консистентный дизайн
- Нет конфликтов имен классов
- Purging неиспользуемых стилей

### CSS Variables для темизации

```css
/* app/globals.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 47.4% 11.2%;
  --primary: 221.2 83.2% 53.3%;
}

[data-theme='dark'] {
  --background: 224 71% 4%;
  --foreground: 213 31% 91%;
}
```

### Компонентные стили (редко)

Только для сложных анимаций или специфических стилей:

```typescript
// Используем CSS Modules или Tailwind @apply если необходимо
```

## Data Fetching

### Server Components (рекомендуется)

```typescript
// Прямой fetch на сервере
export default async function Page() {
  const data = await fetch('http://localhost:8000/api/v1/stats')
  const stats = await data.json()

  return <Dashboard stats={stats} />
}
```

### Client Components (для интерактивности)

```typescript
'use client'

import { useEffect, useState } from 'react'
import { getStats } from '@/lib/api'

export function DashboardClient() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getStats({ period: 90 }).then(setStats)
  }, [])

  if (!stats) return <Skeleton />
  return <Dashboard stats={stats} />
}
```

### API Routes (проксирование)

```typescript
// app/api/stats/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const period = searchParams.get('period') || '90'

  const response = await fetch(
    `http://localhost:8000/api/v1/stats?period=${period}`
  )

  return Response.json(await response.json())
}
```

**Когда использовать API Routes:**

- Скрытие внутренних API
- Добавление аутентификации
- Трансформация данных

## Обработка ошибок

### Error Boundaries

```typescript
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>Что-то пошло не так!</h2>
      <button onClick={() => reset()}>Попробовать снова</button>
    </div>
  )
}
```

### Graceful degradation

```typescript
try {
  const stats = await getStats({ period: 90 })
  return <Dashboard stats={stats} />
} catch (error) {
  console.error('Failed to load stats:', error)
  return <ErrorMessage />
}
```

## Производительность

### Оптимизация изображений

```typescript
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={200}
  priority // для важных изображений
/>
```

### Code splitting (автоматический)

Next.js автоматически разделяет код по страницам.

### Dynamic imports (при необходимости)

```typescript
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('@/components/chart'), {
  loading: () => <Skeleton />,
})
```

## Доступность (a11y)

shadcn/ui основан на Radix UI, который обеспечивает доступность из коробки:

- Keyboard navigation
- ARIA attributes
- Screen reader support
- Focus management

**Наши обязательства:**

- Семантический HTML
- Alt текст для изображений
- Контрастные цвета
- Keyboard-first navigation

## Тестирование (планируется)

### Unit тесты (Vitest)

```typescript
describe('StatsCard', () => {
  it('renders value correctly', () => {
    render(<StatsCard title="Users" value={100} trend="up" />)
    expect(screen.getByText('100')).toBeInTheDocument()
  })
})
```

### E2E тесты (Playwright)

```typescript
test('dashboard loads stats', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page.getByText('Total Users')).toBeVisible()
})
```

## Будущие улучшения

### Планируется в следующих спринтах

- **React Query** для server state management
- **Zustand** для глобального state (если потребуется)
- **Vitest + React Testing Library** для тестов
- **Playwright** для E2E тестов
- **Storybook** для компонентов в изоляции
- **Dark mode** через next-themes
- **i18n** для мультиязычности (при необходимости)

## Связанные документы

- [ADR-04: Выбор технологического стека](../../doc/adrs/ADR-04.md)
- [Dashboard Requirements](dashboard-requirements.md)
- [Frontend Roadmap](frontend-roadmap.md)

---

**Версия:** 1.0
**Автор:** systtechbot team
**Sprint:** S2 - Инициализация Frontend проекта
