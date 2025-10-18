# Sprint S3 - Быстрый старт

Инструкция по запуску и тестированию Real БД + ИИ-чат с аналитикой.

## Предварительные требования

1. PostgreSQL запущен и доступен
2. База данных создана и миграции применены
3. `.env` файл настроен с необходимыми переменными
4. Python зависимости установлены
5. Node.js зависимости установлены (в `frontend/`)

## Настройка переменных окружения

Добавьте в `.env`:

```bash
# Основные переменные (уже должны быть)
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/systtechbot
TELEGRAM_TOKEN=your_token
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# Новые переменные для API
# API_MODE=real  # По умолчанию real, можно установить "mock" для тестирования
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Для frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Запуск системы

### 1. Запуск Backend API

```bash
# По умолчанию используется Real режим (с реальной БД)
python -m api.main

# Или через uvicorn напрямую
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Для использования Mock данных (для тестирования):
API_MODE=mock python -m api.main
```

**Проверка:**
- Откройте http://localhost:8000/docs для Swagger UI
- Проверьте endpoint `/health` возвращает `{"status": "healthy", "mode": "real"}`

### 2. Запуск Frontend

```bash
cd frontend
pnpm dev
```

**Проверка:**
- Откройте http://localhost:3000
- Должен быть редирект на `/dashboard`
- Dashboard должен показывать реальные данные из БД

## Тестирование Real БД

### 1. Проверка Dashboard

1. Откройте http://localhost:3000/dashboard
2. Убедитесь, что отображаются метрики:
   - Всего пользователей
   - Всего диалогов
   - Всего сообщений
   - Средняя длина сообщения
3. Проверьте график активности
4. Переключите периоды (7, 30, 90 дней)

### 2. Проверка API напрямую

```bash
# Получить статистику за 7 дней
curl http://localhost:8000/api/v1/stats?period=7

# Получить статистику за 90 дней
curl http://localhost:8000/api/v1/stats?period=90
```

## Тестирование ИИ-чата

### 1. Открытие чата

1. Откройте http://localhost:3000/chat
2. Должен отобразиться интерфейс чата с приветствием

### 2. Базовые тесты

Попробуйте следующие запросы:

**Тест 1: Простой подсчет**
```
Вопрос: Сколько всего пользователей?
Ожидается: Ответ с числом пользователей из БД
```

**Тест 2: Агрегация**
```
Вопрос: Какая средняя длина сообщения?
Ожидается: Число с округлением
```

**Тест 3: Временной срез**
```
Вопрос: Сколько сообщений было отправлено за последние 7 дней?
Ожидается: SQL с фильтром по дате + ответ
```

**Тест 4: Детальный запрос**
```
Вопрос: Покажи топ-5 пользователей по количеству сообщений
Ожидается: SQL с GROUP BY + ORDER BY + LIMIT
```

**Тест 5: Без SQL**
```
Вопрос: Привет! Как дела?
Ожидается: Приветствие без выполнения SQL
```

### 3. Проверка истории

1. Отправьте несколько сообщений
2. Обновите страницу
3. История должна восстановиться
4. Нажмите "Очистить историю"
5. История должна удалиться

### 4. Тестирование через API

```bash
# Отправить сообщение
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Сколько всего пользователей?",
    "history": []
  }'

# Очистить историю
curl -X POST http://localhost:8000/api/v1/chat/clear \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1
  }'
```

## Создание тестовых данных

Если в БД нет данных, создайте тестовые записи:

```sql
-- Создать тестового пользователя
INSERT INTO users (telegram_user_id, first_name, created_at)
VALUES (12345, 'Test User', NOW() - INTERVAL '30 days');

-- Создать тестовый чат
INSERT INTO chats (telegram_chat_id, created_at)
VALUES (67890, NOW() - INTERVAL '30 days');

-- Создать тестовые сообщения
INSERT INTO messages (user_id, chat_id, role, content, length, created_at)
SELECT
  1,
  1,
  'user',
  'Test message ' || generate_series,
  20,
  NOW() - (INTERVAL '1 day' * generate_series)
FROM generate_series(1, 30);
```

## Отладка

### Логи Backend

Backend пишет логи в консоль. Следите за:
- Ошибками подключения к БД
- SQL запросами (в debug режиме)
- Ошибками выполнения SQL

### Логи Frontend

Откройте консоль браузера (F12) для просмотра:
- Ошибок API запросов
- Выполненных SQL (если возвращается в `sql_executed`)
- Состояния компонентов

### Частые проблемы

**Проблема:** Dashboard не показывает данные
- Проверьте `API_MODE=real` в переменных окружения
- Проверьте подключение к БД
- Проверьте наличие данных в таблицах

**Проблема:** Чат не отвечает
- Проверьте `OPENAI_API_KEY` в `.env`
- Проверьте логи backend на ошибки LLM
- Проверьте CORS настройки

**Проблема:** SQL не выполняется
- Проверьте формат SQL в промпте
- Проверьте логи на ошибки парсинга
- Попробуйте переформулировать вопрос

## Мониторинг

### API Health Check

```bash
curl http://localhost:8000/health
```

Должно вернуть:
```json
{
  "status": "healthy",
  "mode": "real"
}
```

### Database Connection

```bash
curl http://localhost:8000/
```

Должно вернуть информацию об API без ошибок.

## Документация

- **API Swagger:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc
- **Chat Guide:** `frontend/doc/chat-guide.md`
- **Frontend Roadmap:** `frontend/doc/frontend-roadmap.md`

## Следующие шаги

После успешного тестирования:

1. ✅ Проверьте все TODO в плане
2. ✅ Убедитесь, что нет ошибок linting
3. ✅ Обновите документацию при необходимости
4. ✅ Создайте коммит с изменениями
5. 🎉 Спринт S3 завершен!

---

**Вопросы?** Смотрите детальную документацию в `sprint-s3-full-implementation.plan.md`

