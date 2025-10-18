# systtechbot Frontend

Веб-интерфейс для проекта systtechbot - AI-ассистента для Telegram.

## Описание

Frontend приложение состоит из двух основных частей:

- **Dashboard** - визуализация статистики диалогов с ботом
- **AI Chat** - веб-интерфейс для взаимодействия с аналитическим помощником

## Технологический стек

- **Framework:** Next.js 15 (App Router)
- **Язык:** TypeScript
- **UI Library:** shadcn/ui (Radix UI + Tailwind CSS)
- **Styling:** Tailwind CSS
- **Пакетный менеджер:** pnpm

## Требования

- Node.js >= 18.17
- pnpm (установка: `npm install -g pnpm`)
- Backend API (запущен на `http://localhost:8000`)

## Установка

```bash
# Клонирование репозитория
cd systtechbot/frontend

# Установка зависимостей
pnpm install

# Настройка переменных окружения
cp .env.example .env.local
# Отредактируйте .env.local при необходимости
```

## Команды

### Разработка

```bash
# Запуск dev сервера (с Turbopack)
pnpm dev
```

Приложение будет доступно по адресу: http://localhost:3000

### Сборка

```bash
# Production сборка
pnpm build

# Запуск production версии
pnpm start
```

### Проверка качества

```bash
# Линтинг кода
pnpm lint

# Форматирование кода
pnpm format

# Проверка типов TypeScript
pnpm type-check
```

## Структура проекта

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Главная страница
│   ├── dashboard/           # Страница дашборда
│   │   └── page.tsx
│   ├── chat/                # Страница AI-чата
│   │   └── page.tsx
│   └── api/                 # API routes
│       └── stats/
│           └── route.ts
├── components/              # React компоненты
│   ├── ui/                  # shadcn/ui компоненты
│   ├── dashboard/           # Компоненты дашборда
│   └── chat/                # Компоненты чата
├── lib/                     # Утилиты и хелперы
│   ├── api.ts              # API client для backend
│   └── utils.ts            # Общие утилиты (shadcn)
├── types/                   # TypeScript типы
│   └── api.ts              # Типы API responses
├── public/                  # Статические файлы
└── doc/                     # Документация
    ├── dashboard-requirements.md
    ├── frontend-roadmap.md
    └── frontend-vision.md
```

## Соглашения по коду

### Именование

- **Компоненты:** PascalCase (`UserCard.tsx`)
- **Файлы:** kebab-case для утилит (`api-client.ts`)
- **Переменные и функции:** camelCase (`getUserData`)
- **Типы и интерфейсы:** PascalCase (`UserData`, `ApiResponse`)

### TypeScript

- Используем строгий режим (`strict: true`)
- Явная типизация для публичных API
- Выводимые типы для внутренних переменных

### Стилизация

- Tailwind CSS utility-first подход
- CSS variables для темизации
- Избегаем inline styles без необходимости

### Компоненты

- React Server Components по умолчанию
- 'use client' только когда необходимо
- Композиция над наследованием
- Небольшие, переиспользуемые компоненты

## Разработка

### Добавление компонентов shadcn/ui

```bash
# Просмотр доступных компонентов
pnpm dlx shadcn@latest add

# Добавление конкретного компонента
pnpm dlx shadcn@latest add button
```

Компоненты копируются в `components/ui/` и могут быть свободно модифицированы.

### Работа с API

API client находится в `lib/api.ts`. Все типы API определены в `types/api.ts`.

Пример использования:

```typescript
import { getStats } from '@/lib/api'

const stats = await getStats({ period: 30 })
```

### Переменные окружения

Публичные переменные (доступные в браузере) должны начинаться с `NEXT_PUBLIC_`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Развертывание

### Docker (планируется)

```bash
docker build -t systtechbot-frontend .
docker run -p 3000:3000 systtechbot-frontend
```

### Vercel (опционально)

Проект совместим с развертыванием на Vercel:

```bash
vercel deploy
```

## Документация

- [Функциональные требования к дашборду](doc/dashboard-requirements.md)
- [Frontend roadmap](doc/frontend-roadmap.md)
- [Техническое видение](doc/frontend-vision.md)
- [ADR-04: Выбор технологического стека](../doc/adrs/ADR-04.md)

## Связанные проекты

- Backend API: `../api/`
- Telegram Bot: `../`

## Лицензия

Приватный проект systtechbot team.

---

**Версия:** 0.1.0
**Статус:** S2 - Инициализация (Завершен)
**Следующий спринт:** S3 - Реализация Dashboard
