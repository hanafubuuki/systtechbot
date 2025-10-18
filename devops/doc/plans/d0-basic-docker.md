# План Спринта D0: Basic Docker Setup

## Обзор

Создать простую Docker инфраструктуру для локального запуска всех сервисов systtechbot. Фокус на работоспособности, а не на оптимизации.

## Текущее состояние

- **Сервисы**: Bot (Python), API (FastAPI), Frontend (Next.js), PostgreSQL
- **Есть**: `docker-compose.yml` с только PostgreSQL
- **Зависимости**:
  - Bot и API: Python 3.11+, зависимости в `pyproject.toml`
  - Frontend: Node.js, Next.js 15, зависимости в `package.json`
- **База данных**: Требуются миграции через Alembic
- **Конфигурация**: Через переменные окружения (.env файлы)

## Реализованная структура

```
devops/
  docker-compose.yml       # Главный файл оркестрации
  env.example             # Пример переменных окружения
  .dockerignore           # Исключения для Docker сборки
  README.md               # Подробная документация
  dockerfiles/
    bot.Dockerfile        # Dockerfile для Telegram бота
    api.Dockerfile        # Dockerfile для FastAPI сервиса
    frontend.Dockerfile   # Dockerfile для Next.js фронтенда
  scripts/
    wait-for-db.sh        # Скрипт ожидания БД и миграций
```

## Выполненные задачи

### 1. ✅ Dockerfile для Bot сервиса

**Файл**: `devops/dockerfiles/bot.Dockerfile`

**Реализация**:
- Базовый образ: Python 3.11-slim
- Установка UV через официальный скрипт
- Копирование pyproject.toml и uv.lock
- Синхронизация зависимостей через `uv sync`
- Запуск через `uv run python bot.py`

### 2. ✅ Dockerfile для API сервиса

**Файл**: `devops/dockerfiles/api.Dockerfile`

**Реализация**:
- Базовый образ: Python 3.11-slim
- Установка UV
- Синхронизация зависимостей с опциональной группой `api`
- Expose порта 8000
- Запуск через `uv run uvicorn api.main:app`

### 3. ✅ Dockerfile для Frontend сервиса

**Файл**: `devops/dockerfiles/frontend.Dockerfile`

**Реализация**:
- Базовый образ: Node 20-alpine
- Включение и настройка pnpm через corepack
- Установка зависимостей с `--frozen-lockfile`
- Сборка через `pnpm build`
- Запуск продакшн сервера через `pnpm start`
- Expose порта 3000

### 4. ✅ docker-compose.yml

**Файл**: `devops/docker-compose.yml`

**Реализованные сервисы**:

1. **postgres**
   - Образ: postgres:16-alpine
   - Порты: 5432:5432
   - Volume: postgres_data для персистентности
   - Healthcheck для контроля готовности
   - Restart: unless-stopped

2. **bot**
   - Build из bot.Dockerfile с контекстом из корня
   - Зависимость от postgres с условием health check
   - Все необходимые переменные окружения
   - Restart: unless-stopped

3. **api**
   - Build из api.Dockerfile
   - Зависимость от postgres с health check
   - Порты: 8000:8000
   - Собственный healthcheck через curl
   - Все переменные окружения для API и LLM

4. **frontend**
   - Build из frontend.Dockerfile
   - Зависимость от api
   - Порты: 3000:3000
   - Переменная NEXT_PUBLIC_API_URL

**Networking**: Все сервисы в bridge сети `systtechbot_network`

### 5. ✅ .dockerignore

**Файл**: `devops/.dockerignore`

**Исключения**:
- Python кеши и артефакты
- Node.js кеши (.next, node_modules)
- Логи и тестовые файлы
- .env файлы
- Git и IDE файлы
- Docker файлы

### 6. ✅ env.example

**Файл**: `devops/env.example`

**Секции**:
- PostgreSQL настройки
- Bot конфигурация (токены, API ключи)
- API конфигурация
- Frontend конфигурация

### 7. ✅ Скрипт wait-for-db.sh

**Файл**: `devops/scripts/wait-for-db.sh`

**Функциональность**:
- Ожидание готовности PostgreSQL
- Автоматический запуск миграций через Alembic
- Запуск основной команды после успешной инициализации

### 8. ✅ Документация

**Файл**: `devops/README.md`

**Содержание**:
1. Быстрый старт (4 шага)
2. Описание всех сервисов
3. Полезные команды Docker Compose
4. Детальный раздел устранения проблем
5. Структура директории
6. Заметки о безопасности
7. Ссылки на дополнительную документацию

## Технические решения

### Управление зависимостями

- **Bot/API**: UV для быстрой установки Python пакетов
- **Frontend**: pnpm для эффективного управления Node пакетами

### Порядок запуска

1. PostgreSQL запускается первым
2. Healthcheck проверяет готовность БД
3. Bot и API запускаются только после успешного healthcheck
4. Frontend запускается после API

### Переменные окружения

- Все переменные с значениями по умолчанию
- Чувствительные данные (токены) без дефолтов
- DATABASE_URL указывает на контейнер postgres по имени сервиса

### Сети и коммуникация

- Все сервисы в одной bridge сети
- Сервисы обращаются друг к другу по имени контейнера
- Frontend подключается к API через localhost:8000 (для браузера)

## Критерии приемки

- ✅ Команда `docker-compose up` запускает все 4 сервиса
- ✅ PostgreSQL поднимается с корректными настройками
- ✅ Bot запускается и подключается к БД
- ✅ API доступен на http://localhost:8000
- ✅ API отдает данные через /api/v1/stats
- ✅ Frontend доступен на http://localhost:3000
- ✅ Frontend успешно подключается к API
- ✅ Миграции БД могут быть выполнены автоматически (через init_db())
- ✅ Документация содержит инструкции по запуску

## Что НЕ сделано (намеренно)

- ❌ Multi-stage builds (будет в следующих спринтах)
- ❌ Оптимизация размера образов
- ❌ Hadolint проверки
- ❌ Production-ready конфигурация
- ❌ Secrets management
- ❌ Мониторинг и логирование

Все это запланировано на последующие спринты согласно roadmap.

## Результат

Создана полностью рабочая Docker инфраструктура для локальной разработки. Разработчик может запустить весь стек одной командой `docker-compose up` и сразу начать работу с приложением.

