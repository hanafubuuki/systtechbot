# Quick Start - systtechbot Full Stack

Полное руководство по запуску systtechbot: PostgreSQL + Backend API + Frontend

---

## Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- pnpm (для frontend)
- uv (для Python зависимостей)

---

## 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/systtechbot

# Telegram Bot
TELEGRAM_TOKEN=your_telegram_bot_token

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TIMEOUT=30

# LLM Settings
MAX_TOKENS=1000
TEMPERATURE=0.7
MAX_CONTEXT_MESSAGES=10

# API Settings (по умолчанию real режим)
# API_MODE=real  # можно установить "mock" для тестирования
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 2. Запуск PostgreSQL

### Через Docker (рекомендуется)

```bash
docker run -d \
  --name systtechbot-postgres \
  -e POSTGRES_USER=systtechbot \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=systtechbot \
  -p 5432:5432 \
  postgres:14
```

### Или используйте локальный PostgreSQL

Создайте базу данных:

```sql
CREATE DATABASE systtechbot;
```

---

## 3. Применение миграций

```bash
# Применить миграции Alembic
uv run alembic upgrade head
```

Проверка:
```bash
# Должны быть созданы таблицы: users, chats, messages
psql -U systtechbot -d systtechbot -c "\dt"
```

---

## 4. Создание тестовых данных (опционально)

Если база пустая, создайте тестовые данные:

```bash
uv run python scripts/create_test_data.py
```

Это создаст:
- 10 тестовых пользователей
- 10 тестовых чатов
- ~2000 сообщений за 90 дней

---

## 5. Запуск Backend API

### Через терминал 1:

```bash
# По умолчанию использует real режим (PostgreSQL)
uv run python -m api.main

# Или через uvicorn напрямую
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Проверка:**
- API: http://localhost:8000
- Health: http://localhost:8000/health (должно быть `{"status": "healthy", "mode": "real"}`)
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 6. Запуск Frontend

### Через терминал 2:

```bash
cd frontend

# Установка зависимостей (если еще не установлены)
pnpm install

# Запуск dev сервера
pnpm dev
```

**Проверка:**
- Frontend: http://localhost:3000
- Автоматический редирект на: http://localhost:3000/dashboard

---

## 7. Запуск Telegram Bot (опционально)

### Через терминал 3:

```bash
uv run python bot.py
```

---

## 🧪 Проверка работоспособности

### 1. Dashboard

1. Откройте http://localhost:3000/dashboard
2. Проверьте:
   - ✅ 4 карточки метрик отображаются
   - ✅ Значения из PostgreSQL (не mock)
   - ✅ График активности за 7/30/90 дней
   - ✅ Переключение периодов работает
   - ✅ Темная/светлая тема переключается

### 2. Daily Reporter Chat

1. Откройте http://localhost:3000/chat
2. Проверьте:
   - ✅ Welcome сообщение "Daily Reporter"
   - ✅ Можно задавать любые вопросы
   - ✅ Для сотрудников systtech - вопросы о задачах
   - ✅ История сохраняется
   - ✅ Кнопка "Очистить историю" работает

**Примеры вопросов:**
- "Привет! Расскажи что ты умеешь"
- "Над какими задачами я работал сегодня?"
- "Сколько всего пользователей в системе?"
- "Покажи активность за последнюю неделю"

### 3. API

Проверьте endpoints через curl или Swagger UI:

```bash
# Статистика
curl http://localhost:8000/api/v1/stats?period=7

# Чат
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Сколько всего пользователей?",
    "history": []
  }'
```

### 4. Навигация

- ✅ Кнопка "Dashboard" в navbar ведет на /dashboard
- ✅ Кнопка "Chat" в navbar ведет на /chat
- ✅ Логотип "systtechbot" ведет на / (редирект на /dashboard)
- ✅ Активная страница подсвечена

---

## 🔧 Проверка качества кода

### Python - ruff + mypy

```bash
# Проверка стиля (ruff)
uv run ruff check . --select=E,F,W,I --ignore=E501

# Автоматическое исправление
uv run ruff check . --select=E,F,W,I --ignore=E501 --fix

# Проверка типов (mypy)
uv run mypy . --ignore-missing-imports --no-strict-optional
```

### Frontend - ESLint + TypeScript

```bash
cd frontend

# Проверка TypeScript
pnpm tsc --noEmit

# Проверка ESLint (если настроен)
pnpm lint
```

---

## 📁 Структура проекта

```
systtechbot/
├── api/                        # Backend API (FastAPI)
│   ├── collectors/
│   │   ├── base.py            # Базовый интерфейс
│   │   ├── mock.py            # Mock данные
│   │   └── real.py            # Real данные из PostgreSQL
│   ├── main.py                # FastAPI app + endpoints
│   ├── config.py              # Конфигурация API
│   └── models.py              # Pydantic модели
│
├── services/                  # Бизнес-логика
│   ├── analytics.py           # Text-to-SQL обработка
│   ├── database.py            # PostgreSQL queries
│   ├── llm.py                 # OpenAI интеграция
│   └── context.py             # История диалогов
│
├── roles/
│   └── prompts.py             # Системные промпты (Daily Reporter)
│
├── frontend/                  # Next.js Frontend
│   ├── app/
│   │   ├── dashboard/         # Dashboard страница
│   │   └── chat/              # Daily Reporter чат
│   ├── components/
│   │   ├── dashboard/         # Компоненты дашборда
│   │   └── chat/              # Компоненты чата
│   ├── lib/
│   │   ├── api.ts             # API клиент
│   │   └── formatters.ts      # Утилиты форматирования
│   └── types/
│       └── api.ts             # TypeScript типы
│
├── bot.py                     # Telegram Bot
├── alembic/                   # Миграции БД
└── scripts/
    └── create_test_data.py    # Генератор тестовых данных
```

---

## 🐛 Устранение проблем

### Backend не запускается

**Проблема:** `DATABASE_URL не установлен`
**Решение:** Проверьте `.env` файл, убедитесь что `DATABASE_URL` правильный

**Проблема:** `Failed to connect to database`
**Решение:**
1. Проверьте что PostgreSQL запущен
2. Проверьте credentials в `DATABASE_URL`
3. Проверьте что БД создана

### Frontend показывает ошибки

**Проблема:** `Failed to fetch stats`
**Решение:**
1. Проверьте что Backend API запущен на порту 8000
2. Проверьте `NEXT_PUBLIC_API_URL` в `.env`
3. Проверьте CORS настройки в `api/config.py`

**Проблема:** Dashboard показывает mock данные
**Решение:**
1. Проверьте что API запущен в real режиме (проверьте `/health`)
2. Убедитесь что в `.env` не установлено `API_MODE=mock`

### Chat не работает

**Проблема:** Chat не отвечает
**Решение:**
1. Проверьте `OPENAI_API_KEY` в `.env`
2. Проверьте логи Backend на ошибки LLM
3. Проверьте что `DATABASE_URL` правильный

**Проблема:** SQL не выполняется
**Решение:**
1. Проверьте логи на синтаксические ошибки SQL
2. Попробуйте переформулировать вопрос
3. Убедитесь что таблицы содержат данные

---

## 🚀 Режимы работы

### Development (по умолчанию)

- Backend: Hot reload через `--reload`
- Frontend: Hot reload через `pnpm dev`
- Real режим с PostgreSQL

### Mock режим (для тестирования без БД)

```bash
# В .env или переменная окружения
API_MODE=mock uv run python -m api.main
```

### Production

```bash
# Backend
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
pnpm build
pnpm start
```

---

## 📚 Документация

- **API Docs:** http://localhost:8000/docs
- **Chat Guide:** `frontend/doc/chat-guide.md`
- **Sprint S3 Plan:** `sprint-s3-full-implementation.plan.md`
- **Sprint S3 Summary:** `SPRINT_S3_SUMMARY.md`
- **Changes Log:** `CHANGES_DAILY_REPORTER.md`

---

## 📊 Мониторинг

```bash
# Health check
curl http://localhost:8000/health

# Версия API
curl http://localhost:8000/

# Статистика
curl http://localhost:8000/api/v1/stats?period=90
```

---

## ✨ Особенности

- ✅ **Real-time data** из PostgreSQL
- ✅ **Daily Reporter** - универсальный AI ассистент
- ✅ **Text-to-SQL** - автоматическая генерация запросов
- ✅ **История диалогов** - сохранение и восстановление
- ✅ **Темная/светлая тема** - с сохранением выбора
- ✅ **Responsive design** - адаптивный интерфейс
- ✅ **Type-safe** - TypeScript + Pydantic
- ✅ **Modern stack** - Next.js 15 + FastAPI

---

**Дата:** 2025-10-17
**Версия:** 2.0
**Статус:** Production Ready 🎉
