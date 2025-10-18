# 🤖 systtechbot

[![Build Status](https://github.com/hanafubuuki/systtechbot/actions/workflows/build.yml/badge.svg)](https://github.com/hanafubuuki/systtechbot/actions/workflows/build.yml)

AI-ассистент в виде Telegram бота на базе LLM. Простой, понятный MVP для ведения диалогов с пользователями.

## 📋 Описание

Telegram бот с интеграцией LLM (через OpenRouter/OpenAI-совместимое API), который:
- Ведет диалог с пользователями, сохраняя контекст беседы
- **Хранит историю диалогов в PostgreSQL** (персистентность между перезапусками)
- Работает в заданной роли (настраиваемые промпты)
- Устойчив к ошибкам (graceful degradation)
- Логирует все действия для отладки
- Протестирован (72 unit-теста)

## 📸 Скриншоты

<p align="center">
  <img src="doc/images/photo_2025-10-10_18-41-20.jpg" alt="Девиз" width="400"/>
  <img src="doc/images/photo_2025-10-10_19-56-32.jpg" alt="Пример работы бота" width="400"/>
</p>

*Примеры работы бота: персонализированное приветствие, оценка работы, сохранение контекста диалога, команды /start, /help и /clear*

## ✨ Возможности

- 💬 Ведение диалога с сохранением истории (до 10 сообщений)
- 💾 **Персистентное хранение** в PostgreSQL (soft delete, метаданные сообщений)
- 🎭 Настраиваемые роли через system prompts
- 🔄 Команды: `/start`, `/help`, `/clear`
- 📊 Структурированное логирование
- ⚡ Асинхронная обработка
- 🛡️ Обработка всех типов ошибок LLM API
- ✅ Полное покрытие тестами (72 теста)

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется) 🐳

Самый простой способ запустить все сервисы одной командой:

1. **Перейдите в директорию devops:**
   ```bash
   cd devops
   ```

2. **Скопируйте и настройте переменные окружения:**
   ```bash
   cp env.example .env
   # Отредактируйте .env и заполните TELEGRAM_TOKEN и OPENAI_API_KEY
   ```

3. **Запустите все сервисы:**
   ```bash
   docker-compose up
   ```

После запуска доступны:
- 🤖 **Bot** - работает в фоне
- 🌐 **Frontend** - http://localhost:3000
- 📊 **API** - http://localhost:8000/docs
- 🗄️ **PostgreSQL** - localhost:5432

**Подробнее:** См. [devops/README.md](devops/README.md)

---

### Вариант 2: Локальная разработка

### Требования

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (современный менеджер пакетов)
- [Docker](https://www.docker.com/) и Docker Compose (для PostgreSQL)
- Telegram Bot Token (от [@BotFather](https://t.me/BotFather))
- OpenAI API Key или OpenRouter API Key

### Установка

1. **Клонировать репозиторий:**
   ```bash
   git clone https://github.com/hanafubuuki/systtechbot.git
   cd systtechbot
   ```

2. **Установить зависимости:**
   ```bash
   make install
   ```

   Или вручную:
   ```bash
   uv venv
   uv sync
   ```

3. **Настроить `.env` файл:**
   ```bash
   cp .env.example .env
   ```

   Заполните `.env`:
   ```ini
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_or_openrouter_api_key_here
   DATABASE_URL=postgresql://user:password@localhost:5432/systtechbot_db

   # Опционально (для OpenRouter):
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   OPENAI_MODEL=openai/gpt-oss-20b:free
   ```

4. **Запустить PostgreSQL через Docker:**
   ```bash
   make db-up
   ```

   Или вручную:
   ```bash
   docker-compose up -d
   ```

5. **Применить миграции базы данных:**
   ```bash
   make db-migrate
   ```

   Или вручную:
   ```bash
   uv run alembic upgrade head
   ```

6. **Запустить бота:**
   ```bash
   make run
   ```

   Или вручную:
   ```bash
   uv run bot.py
   ```

## 📚 Гайды и документация

**Полные пошаговые руководства:** [doc/guides/](doc/guides/)

### Быстрый старт
- 🚀 [Getting Started](doc/guides/01-GETTING_STARTED.md) — от клонирования до работающего бота за 5 минут

### Понимание системы
- 📐 [Архитектура](doc/guides/02-ARCHITECTURE.md) — трёхслойная архитектура, поток данных
- 📊 [Модель данных](doc/guides/03-DATA_MODEL.md) — структуры данных (Message, Config, Context)
- 🎨 [Визуальный гайд](doc/guides/05-VISUAL_GUIDE.md) — 13 диаграмм проекта (для визуалов) ⭐

### Разработка
- 🛠️ [Development](doc/guides/04-DEVELOPMENT.md) — workflow, тестирование, проверки качества

**Время на полный онбординг:** ~60 минут (или 20 минут для визуального погружения)

## 💾 База данных

Проект использует **PostgreSQL** для персистентного хранения истории диалогов.

**Основные возможности:**
- 🔄 Soft delete — данные не удаляются физически, только помечаются как удалённые
- 📊 Метаданные сообщений — дата создания (`created_at`) и длина в символах (`length`)
- 🐳 Docker Compose — простое развёртывание локального окружения
- 🔄 Alembic — управление миграциями схемы БД
- 🎯 Raw SQL — прозрачный доступ к данным без "магии" ORM

**Подробная документация:** [doc/guides/06-DATABASE.md](doc/guides/06-DATABASE.md)

**Управление базой данных:**
```bash
make db-up       # Запустить PostgreSQL
make db-down     # Остановить PostgreSQL
make db-migrate  # Применить миграции
make db-reset    # Сбросить БД и применить миграции заново
```

**Архитектурные решения:** [doc/adrs/ADR-03.md](doc/adrs/ADR-03.md) (выбор PostgreSQL, Alembic, Raw SQL)

## 🌐 Frontend (Web-интерфейс)

Проект включает **веб-интерфейс** для визуализации статистики и взаимодействия с AI-ассистентом.

**Основные компоненты:**
- 📊 **Dashboard** — визуализация метрик диалогов (пользователи, сообщения, графики активности)
- 💬 **AI Chat** — веб-интерфейс для аналитического помощника (text-to-SQL запросы)

**Технологический стек:**
- ⚛️ **Next.js 15** (App Router) — React фреймворк с SSR
- 📘 **TypeScript** — типобезопасность
- 🎨 **shadcn/ui** — компоненты на Radix UI + Tailwind CSS
- 🐱 **pnpm** — быстрый пакетный менеджер

**Быстрый старт:**
```bash
# Перейти в директорию frontend
cd frontend

# Установить зависимости
pnpm install

# Запустить dev сервер
pnpm dev
```

Интерфейс доступен по адресу: http://localhost:3000

**Документация:**
- 📋 [Frontend README](frontend/README.md) — подробное описание и команды
- 📐 [Frontend Vision](frontend/doc/frontend-vision.md) — архитектура и принципы
- 📊 [Dashboard Requirements](frontend/doc/dashboard-requirements.md) — требования к дашборду
- 🗺️ [Frontend Roadmap](frontend/doc/frontend-roadmap.md) — план разработки
- 🎯 [ADR-04](doc/adrs/ADR-04.md) — выбор технологического стека

**Статус:** Спринт S2 завершен (инициализация проекта). Реализация дашборда запланирована на S3.

## 📦 Команды Makefile

```bash
# Разработка
make install    # Установить зависимости
make run        # Запустить бота
make test       # Запустить тесты
make clean      # Очистить временные файлы

# База данных
make db-up      # Запустить PostgreSQL через Docker
make db-down    # Остановить PostgreSQL
make db-migrate # Применить миграции
make db-reset   # Сбросить БД и применить миграции заново

# Качество кода
make format     # Форматировать код (ruff)
make lint       # Проверить линтером (ruff)
make typecheck  # Проверить типы (mypy)
make coverage   # Тесты с покрытием
make quality    # Полная проверка качества
```

## 🎮 Запуск через Cursor/VS Code UI

Проект настроен для удобной работы через UI Cursor:

### Быстрый запуск (Tasks)

**Нажми `Ctrl+Shift+P` и выбери:**
- 🚀 **Run Bot** — запустить бота
- 🧪 **Run All Tests** — все тесты
- ✅ **Quality Check** — полная проверка качества

Или нажми `Ctrl+Shift+B` для быстрого запуска тестов.

### Отладка (Debug)

**Нажми `F5` и выбери:**
- 🚀 **Run Bot** — запуск с отладкой
- 🧪 **Debug Current Test File** — отладка текущего теста
- 🧪 **Debug All Tests** — отладка всех тестов

**Горячие клавиши:**
- `F9` — установить breakpoint
- `F5` — запустить/продолжить
- `F10` — шаг через (step over)
- `F11` — шаг в функцию (step into)

### Testing панель

1. Открой боковую панель "Testing" (иконка колбочки)
2. Увидишь все тесты в дереве
3. Кликни "▶" рядом с тестом для запуска
4. Кликни правой кнопкой → "Debug Test" для отладки

**Подробнее:** См. [`.vscode/README.md`](.vscode/README.md)

## 🎯 Использование

### Команды бота

- `/start` - Начать общение с ботом
- `/help` - Показать справку по командам
- `/clear` - Очистить историю диалога

### Примеры диалогов

```
👤 Пользователь: Привет!
🤖 Бот: Привет! Чем могу помочь?

👤 Пользователь: Столица России?
🤖 Бот: Москва

👤 Пользователь: А население?
🤖 Бот: Население Москвы составляет около 13 миллионов человек
```

## 🧪 Тестирование

Запустить все тесты:
```bash
make test
```

Или напрямую через pytest:
```bash
uv run pytest tests/ -v
```

**Покрытие тестами:**
- ✅ Команды бота (10 тестов)
- ✅ Контекст диалога (13 тестов, включая parametrized)
- ✅ LLM сервис (9 тестов)
- ✅ Промпты (7 тестов)
- ✅ Конфигурация (8 тестов)
- ✅ Интеграционные тесты handlers (11 тестов)
- ✅ Слой доступа к данным (7 тестов)
- ✅ Другие тесты (7 тестов)
- **Всего: 72 теста, coverage: 80%+**

## 🔍 Контроль качества

Проект использует автоматизированные инструменты для поддержания качества кода:

### Команды

```bash
# Форматирование кода (ruff)
make format

# Проверка линтером (ruff)
make lint

# Проверка типов (mypy)
make typecheck

# Тесты с покрытием
make coverage

# Полная проверка качества (format + lint + typecheck + test)
make quality
```

### Стандарты качества

- ✅ **Форматирование:** `ruff format` (line length: 100)
- ✅ **Линтинг:** `ruff check` (pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade)
- ✅ **Типизация:** `mypy --strict` (disallow_untyped_defs)
- ✅ **Тесты:** `pytest` с coverage >= 80%

### Перед коммитом

```bash
# Одна команда для всех проверок
make quality
```

Все проверки должны проходить без ошибок! ✅

## 📁 Структура проекта

```
systtechbot/
├── bot.py                 # Точка входа
├── config.py              # Конфигурация
├── constants.py           # Константы (Enums)
├── message_types.py       # Типы данных (TypedDict)
├── handlers/              # Обработчики Telegram
│   ├── commands.py        # Команды (/start, /help, /clear)
│   └── messages.py        # Текстовые сообщения
├── services/              # Бизнес-логика
│   ├── llm.py            # Работа с LLM API
│   ├── context.py        # Управление контекстом
│   ├── database.py       # Слой доступа к данным (DAL)
│   └── analytics.py      # Аналитические запросы
├── roles/                 # Промпты и роли
│   └── prompts.py
├── api/                   # FastAPI сервис
│   ├── main.py           # Основное приложение API
│   ├── config.py         # Конфигурация API
│   ├── models.py         # Pydantic модели
│   └── collectors/       # Коллекторы данных
├── frontend/              # Next.js веб-интерфейс
│   ├── app/              # App Router страницы
│   ├── components/       # React компоненты
│   └── lib/              # Утилиты и API клиент
├── alembic/               # Миграции базы данных
│   ├── versions/         # Файлы миграций
│   └── env.py            # Конфигурация Alembic
├── devops/                # Docker и CI/CD
│   ├── docker-compose.yml  # Оркестрация сервисов
│   ├── dockerfiles/       # Dockerfiles для сервисов
│   ├── scripts/          # Вспомогательные скрипты
│   └── doc/              # DevOps документация
├── tests/                 # Тесты
│   ├── test_commands.py
│   ├── test_context.py
│   ├── test_database.py  # Тесты DAL
│   ├── test_llm.py
│   └── test_prompts.py
└── doc/                   # Документация
    ├── vision.md          # Техническое видение
    ├── roadmap.md         # План разработки
    ├── guides/            # Пошаговые руководства
    └── adrs/              # Architecture Decision Records
```

## ⚙️ Конфигурация

Все параметры настраиваются через `.env` файл:

```ini
# Обязательные
TELEGRAM_TOKEN=           # Токен Telegram бота
OPENAI_API_KEY=          # API ключ для LLM
DATABASE_URL=            # URL подключения к PostgreSQL

# Опциональные
OPENAI_BASE_URL=https://api.openai.com/v1  # URL API (для OpenRouter и др.)
OPENAI_MODEL=gpt-4o-mini                    # Модель LLM
MAX_TOKENS=1000                             # Макс. токенов в ответе
TEMPERATURE=0.7                             # Температура генерации
MAX_CONTEXT_MESSAGES=10                     # Макс. сообщений в контексте
OPENAI_TIMEOUT=30                           # Таймаут запроса (сек)
```

**Пример `DATABASE_URL`:**
```
postgresql://user:password@localhost:5432/systtechbot_db
```

## 📝 Логирование

Все действия логируются в `bot.log` и консоль:

```
2025-10-10 19:35:39 - handlers.commands - INFO - User 12345 started conversation: user_name=John, chat_id=67890
2025-10-10 19:35:46 - handlers.messages - INFO - User 12345 sent message: length=25, chat_id=67890
2025-10-10 19:35:47 - services.llm - INFO - LLM request: model=gpt-4o-mini, messages_count=2
2025-10-10 19:35:49 - services.llm - INFO - LLM response: length=150
2025-10-10 19:35:49 - handlers.messages - INFO - User 12345 received response: length=150, context_size=3
```

## 🛠️ Технологии

- **Python 3.11+** - язык разработки
- **aiogram 3.x** - фреймворк для Telegram ботов
- **OpenAI Python SDK** - работа с LLM API
- **PostgreSQL** - персистентное хранение данных
- **psycopg3** - асинхронный адаптер для PostgreSQL
- **Alembic** - система миграций базы данных
- **Docker & Docker Compose** - контейнеризация всех сервисов
- **uv** - современный менеджер пакетов
- **pytest** - тестирование
- **FastAPI** - REST API для статистики
- **Next.js 15** - веб-интерфейс дашборда

## 📚 Документация

### Гайды (пошаговые руководства)
- 📘 [Гайды для разработчиков](doc/guides/) — полный онбординг за 60 минут
  - [Getting Started](doc/guides/01-GETTING_STARTED.md) — быстрый старт
  - [Архитектура](doc/guides/02-ARCHITECTURE.md) — понимание системы
  - [Модель данных](doc/guides/03-DATA_MODEL.md) — структуры данных
  - [Development](doc/guides/04-DEVELOPMENT.md) — процесс разработки
  - [Визуальный гайд](doc/guides/05-VISUAL_GUIDE.md) ⭐ — 13 диаграмм проекта

### Техническая документация
- [vision.md](doc/vision.md) - Техническое видение проекта
- [roadmap.md](doc/roadmap.md) - Дорожная карта проекта (спринты)
- [База данных](doc/guides/06-DATABASE.md) - Документация по PostgreSQL и миграциям
- [ADR-01](doc/adrs/ADR-01.md) - Выбор LLM провайдера
- [ADR-02](doc/adrs/ADR-02.md) - Выбор Telegram фреймворка
- [ADR-03](doc/adrs/ADR-03.md) - Стратегия хранения контекста диалогов

### DevOps документация
- 🐳 [Docker Setup](devops/README.md) - Запуск через Docker Compose
- 🗺️ [DevOps Roadmap](devops/doc/devops-roadmap.md) - План DevOps автоматизации
- 📋 [План D0](devops/doc/plans/d0-basic-docker.md) - Детали реализации Docker Setup

## 🔧 Принципы разработки

- **KISS** (Keep It Simple, Stupid) - простота превыше всего
- **YAGNI** (You Aren't Gonna Need It) - только необходимый функционал
- **MVP-first** - работающий код важнее идеального
- **Fail Fast** - явные ошибки лучше скрытых багов

## 📄 Лицензия

MIT

## 👨‍💻 Автор

Разработано как учебный проект для изучения разработки Telegram ботов с LLM интеграцией.

---

**Версия:** 0.1.0 (MVP)
**Дата:** 2025-10-10
