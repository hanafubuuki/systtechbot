# 🤖 systtechbot

AI-ассистент в виде Telegram бота на базе LLM. Простой, понятный MVP для ведения диалогов с пользователями.

## 📋 Описание

Telegram бот с интеграцией LLM (через OpenRouter/OpenAI-совместимое API), который:
- Ведет диалог с пользователями, сохраняя контекст беседы
- Работает в заданной роли (настраиваемые промпты)
- Устойчив к ошибкам (graceful degradation)
- Логирует все действия для отладки
- Протестирован (38 unit-тестов)

## 📸 Скриншоты

<p align="center">
  <img src="doc/images/photo_2025-10-10_18-41-20.jpg" alt="Пример работы бота - диалог" width="400"/>
  <img src="doc/images/photo_2025-10-10_19-56-32.jpg" alt="Пример работы бота - команды" width="400"/>
</p>

*Примеры работы бота: персонализированное приветствие, оценка работы, сохранение контекста диалога, команды /start, /help и /clear*

## ✨ Возможности

- 💬 Ведение диалога с сохранением истории (до 10 сообщений)
- 🎭 Настраиваемые роли через system prompts
- 🔄 Команды: `/start`, `/help`, `/clear`
- 📊 Структурированное логирование
- ⚡ Асинхронная обработка
- 🛡️ Обработка всех типов ошибок LLM API
- ✅ Полное покрытие тестами

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (современный менеджер пакетов)
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
   
   # Опционально (для OpenRouter):
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   OPENAI_MODEL=openai/gpt-oss-20b:free
   ```

4. **Запустить бота:**
   ```bash
   make run
   ```
   
   Или вручную:
   ```bash
   uv run bot.py
   ```

## 📦 Команды Makefile

```bash
make install  # Установить зависимости
make run      # Запустить бота
make test     # Запустить тесты
make clean    # Очистить временные файлы
```

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
- ✅ Контекст диалога (12 тестов)
- ✅ LLM сервис (9 тестов)
- ✅ Промпты (7 тестов)
- **Всего: 38 тестов**

## 📁 Структура проекта

```
systtechbot/
├── bot.py                 # Точка входа
├── config.py              # Конфигурация
├── handlers/              # Обработчики Telegram
│   ├── commands.py        # Команды (/start, /help, /clear)
│   └── messages.py        # Текстовые сообщения
├── services/              # Бизнес-логика
│   ├── llm.py            # Работа с LLM API
│   └── context.py        # Управление контекстом
├── roles/                 # Промпты и роли
│   └── prompts.py        
├── tests/                 # Тесты
│   ├── test_commands.py
│   ├── test_context.py
│   ├── test_llm.py
│   └── test_prompts.py
└── doc/                   # Документация
    ├── vision.md          # Техническое видение
    ├── tasklist.md        # План разработки
    └── adrs/              # Architecture Decision Records
```

## ⚙️ Конфигурация

Все параметры настраиваются через `.env` файл:

```ini
# Обязательные
TELEGRAM_TOKEN=           # Токен Telegram бота
OPENAI_API_KEY=          # API ключ для LLM

# Опциональные
OPENAI_BASE_URL=https://api.openai.com/v1  # URL API (для OpenRouter и др.)
OPENAI_MODEL=gpt-4o-mini                    # Модель LLM
MAX_TOKENS=1000                             # Макс. токенов в ответе
TEMPERATURE=0.7                             # Температура генерации
MAX_CONTEXT_MESSAGES=10                     # Макс. сообщений в контексте
OPENAI_TIMEOUT=30                           # Таймаут запроса (сек)
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
- **uv** - современный менеджер пакетов
- **pytest** - тестирование

## 📚 Документация

- [vision.md](doc/vision.md) - Техническое видение проекта
- [tasklist.md](doc/tasklist.md) - План разработки (7 итераций)
- [ADR-01](doc/adrs/ADR-01.md) - Выбор LLM провайдера
- [ADR-02](doc/adrs/ADR-02.md) - Выбор Telegram фреймворка

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
