# Техническое видение проекта systtechbot

**Цель:** Создать минимально жизнеспособный прототип (MVP) LLM-ассистента в виде Telegram-бота.

**Принцип:** KISS (Keep It Simple, Stupid) — максимальная простота во всем.

---

## 1. Технологии

### Стек

- **Python 3.11+** — основной язык
- **uv** — современный менеджер пакетов (быстрее pip)
- **aiogram 3.x** — фреймворк для Telegram Bot API
- **openai** — SDK для OpenAI API
- **python-dotenv** — конфигурация через .env

### Зависимости (pyproject.toml)

```toml
[project]
name = "systtechbot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "aiogram>=3.0.0,<4.0.0",
    "openai>=1.0.0,<2.0.0",
    "python-dotenv>=1.0.0,<2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
```

### Хранение данных

- **In-Memory** — контекст диалогов в словаре Python
- Без базы данных

### Инфраструктура

- Локальный запуск через Makefile
- Long polling для Telegram
- Без дополнительных сервисов

---

## 2. Принципы разработки

### Основные принципы

- **KISS** — простые решения всегда лучше сложных
- **YAGNI** — только то, что нужно сейчас
- **MVP-first** — сначала работающий прототип, потом улучшения
- **Fail Fast** — быстрая проверка гипотез
- **Код для людей** — читаемость важнее "умности"

### Тестирование

**Уровень: минимальный**

- Критичные функции (OpenAI API, контекст)
- Smoke tests (бот запускается и отвечает)
- Инструмент: `pytest`

### Критерии успеха MVP

- ✅ Бот отвечает на сообщения
- ✅ Помнит контекст диалога
- ✅ Работает в заданной роли
- ✅ Код понятен и легко меняется
- ✅ Запуск за 5 минут

---

## 3. Структура проекта

```
systtechbot/
├── .env                    # Конфигурация
├── .env.example
├── .gitignore
├── pyproject.toml          # Зависимости (uv)
├── uv.lock                 # Lock-файл зависимостей
├── README.md
├── Makefile                # Команды для запуска
│
├── bot.py                  # 🎯 Точка входа
├── config.py               # Настройки
│
├── handlers/               # Обработчики Telegram
│   ├── commands.py         # /start, /help, /clear
│   └── messages.py         # Обработка сообщений
│
├── services/               # Бизнес-логика
│   ├── llm.py             # OpenAI API
│   └── context.py         # Управление контекстом
│
├── roles/                  # Роли бота
│   └── prompts.py         # System prompts
│
├── tests/                  # Тесты
│   ├── test_llm.py
│   └── test_context.py
│
└── doc/                    # Документация
    ├── adrs/               # ADR-01, ADR-02
    ├── conventions.md
    ├── idea.md
    ├── tasklist.md
    ├── vision.md
    └── workflow.md
```

**Размер:** ~500-700 строк кода (без тестов)

---

## 4. Архитектура

### Трехслойная архитектура

```
Telegram User
     ↓
Presentation Layer (handlers/)    ← Прием/отправка сообщений
     ↓
Business Logic Layer (services/)  ← LLM, контекст, роли
     ↓
External Services (OpenAI API)
```

### Поток данных

```
1. User → "Привет!"
2. handlers/messages.py → получает сообщение
3. services/context.py → добавляет в контекст
4. services/llm.py → вызывает OpenAI API
5. services/context.py → сохраняет ответ
6. handlers/messages.py → отправляет ответ
```

### Хранение состояния

**Простой Python словарь:**

```python
# Глобальная структура в services/context.py
user_contexts = {}

# Ключ: (user_id, chat_id)
# Значение: {
#     "messages": [...],
#     "user_name": "Иван",
#     "last_activity": datetime
# }
```

### Обработка ошибок

| Ошибка | Действие |
|--------|----------|
| OpenAI недоступен | "Сервис временно недоступен" |
| Rate limit | "Слишком много запросов" |
| Превышен лимит токенов | Автосжатие контекста |
| Неизвестная | Логирование + "Произошла ошибка" |

**Принцип:** Бот никогда не "падает", всегда отвечает пользователю.

### Ограничения

- Максимум 10 сообщений в контексте
- Timeout OpenAI: 30 секунд
- Без retry-логики (для MVP)

---

## 5. Модель данных

### Контекст диалога

```python
{
    "messages": [
        {"role": "system", "content": "Ты — AI-ассистент..."},
        {"role": "user", "content": "Привет!"},
        {"role": "assistant", "content": "Здравствуйте!"}
    ],
    "user_name": "Иван",
    "last_activity": datetime(...)
}
```

### Роль (одна для MVP)

```python
DEFAULT_SYSTEM_PROMPT = """Ты — полезный AI-ассистент.

ПРАВИЛА:
- Отвечай кратко и по делу
- Будь вежливым и дружелюбным
- Используй markdown для форматирования
- Обращайся к пользователю по имени, если оно известно
"""
```

### Конфигурация

```python
@dataclass
class Config:
    telegram_token: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    max_tokens: int = 1000
    temperature: float = 0.7
    max_context_messages: int = 10
    openai_timeout: int = 30
```

---

## 6. Работа с LLM

### Основной процесс

```python
async def get_llm_response(messages: list, user_name: str = None) -> str:
    """Получить ответ от OpenAI API"""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            timeout=30
        )
        return response.choices[0].message.content
    except openai.RateLimitError:
        return "⚠️ Слишком много запросов"
    except openai.APIError:
        return "❌ Сервис недоступен"
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "❌ Произошла ошибка"
```

### Управление контекстом

```python
def trim_context(messages: list, max_messages: int = 10) -> list:
    """Оставляет system prompt + последние max_messages"""
    if len(messages) <= max_messages + 1:
        return messages
    return [messages[0]] + messages[-(max_messages):]
```

### Персонализация

Если имя известно — добавляется в system prompt:

```python
system_prompt = f"Ты — AI-ассистент. Пользователя зовут {user_name}."
```

---

## 7. Мониторинг и логирование

### Конфигурация

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### Что логируем

```python
# Lifecycle
logger.info("🚀 Bot starting...")
logger.info("✅ Bot started")

# Действия пользователей
logger.info(f"User {user_id} started conversation")
logger.info(f"User {user_id} sent message")

# LLM взаимодействие
logger.info(f"OpenAI request: user_id={user_id}, messages_count={len(messages)}")
logger.info(f"OpenAI response: user_id={user_id}, length={len(response)}")

# Ошибки
logger.error(f"OpenAI error: {type(e).__name__} - {str(e)}")
```

### Уровни логирования

- `INFO` — все важные события
- `ERROR` — только ошибки

### Анализ логов

```bash
# Следить в реальном времени
tail -f bot.log

# Количество запросов
grep "OpenAI request" bot.log | wc -l

# Ошибки
grep "ERROR" bot.log
```

---

## 8. Сценарии работы

### Команды

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу, получить приветствие |
| `/help` | Показать справку |
| `/clear` | Очистить историю диалога |

### Основные сценарии

**1. Первый запуск**
- Пользователь → `/start`
- Бот создает контекст, сохраняет имя, отправляет приветствие

**2. Обычный диалог**
- Пользователь отправляет сообщение
- Бот добавляет в контекст → вызывает OpenAI → отправляет ответ

**3. Длинный диалог**
- При >10 сообщений автоматически усекается контекст
- Пользователь не замечает изменений

**4. Очистка**
- `/clear` → контекст удаляется → "История очищена"

**5. Ошибка API**
- OpenAI недоступен → пользователь получает понятное сообщение

**6. Работа в группе**
- Отдельный контекст для каждого `(user_id, chat_id)`

**7. Рестарт**
- Все контексты теряются (хранятся в памяти)
- Ожидаемое поведение для MVP

### Поведение

- Отвечает на все сообщения (успех или ошибка)
- Сохраняет контекст диалога
- Персонализирует ответы по имени
- В группах ведет отдельные контексты для каждого пользователя

---

## 9. Локальный запуск

### Makefile

```makefile
.PHONY: help install run test clean

help:
	@echo "make install  - Установить зависимости через uv"
	@echo "make run      - Запустить бота"
	@echo "make test     - Запустить тесты"
	@echo "make clean    - Очистить временные файлы"

install:
	uv venv
	uv sync
	cp .env.example .env || true

run:
	uv run bot.py

test:
	uv run pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f bot.log
```

### Быстрый старт

```bash
# 0. Установить uv (если еще нет)
curl -LsSf https://astral.sh/uv/install.sh | sh
# или: pip install uv

# 1. Клонировать
git clone <repo-url>
cd systtechbot

# 2. Установить зависимости
make install

# 3. Настроить .env (добавить токены)
nano .env

# 4. Запустить
make run
```

### Получение токенов

**Telegram:**
1. [@BotFather](https://t.me/BotFather) → `/newbot`
2. Получить токен → добавить в `.env`

**OpenAI:**
1. [platform.openai.com](https://platform.openai.com) → API Keys
2. Create key → добавить в `.env`
3. Пополнить баланс ($5 минимум)

### .env файл

```ini
# Обязательные
TELEGRAM_TOKEN=123456:ABC-DEF...
OPENAI_API_KEY=sk-proj-xxx...

# Опциональные (есть дефолты)
# OPENAI_MODEL=gpt-4o-mini
# MAX_TOKENS=1000
# TEMPERATURE=0.7
# MAX_CONTEXT_MESSAGES=10
```

### .gitignore

```gitignore
# Виртуальное окружение (uv создает .venv)
.venv/

# Секреты
.env

# Логи
bot.log

# Python
__pycache__/
*.pyc
*.pyo

# uv lock файл (опционально, можно коммитить)
# uv.lock
```

---

## 10. Конфигурирование

### Принцип

Конфигурация через **переменные окружения** (.env файл).

### Реализация

```python
from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    telegram_token: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    max_tokens: int = 1000
    temperature: float = 0.7
    openai_timeout: int = 30
    max_context_messages: int = 10

def load_config() -> Config:
    config = Config(
        telegram_token=getenv("TELEGRAM_TOKEN", ""),
        openai_api_key=getenv("OPENAI_API_KEY", ""),
        openai_model=getenv("OPENAI_MODEL", "gpt-4o-mini"),
        max_tokens=int(getenv("MAX_TOKENS", "1000")),
        temperature=float(getenv("TEMPERATURE", "0.7")),
        openai_timeout=int(getenv("OPENAI_TIMEOUT", "30")),
        max_context_messages=int(getenv("MAX_CONTEXT_MESSAGES", "10"))
    )
    
    if not config.telegram_token or not config.openai_api_key:
        raise ValueError("Необходимо установить токены в .env")
    
    return config
```

### Использование

```python
from config import load_config

config = load_config()
bot = Bot(token=config.telegram_token)
```

### Безопасность

- `.env` в `.gitignore` (секреты не в репозитории)
- `.env.example` в репозитории (шаблон)
- Валидация при старте (fail fast)

---

## Заключение

Этот документ описывает **техническое видение MVP** проекта systtechbot — простого LLM-ассистента в виде Telegram-бота.

### Ключевые решения

- Python 3.11+ + aiogram 3.x + OpenAI API
- Хранение в памяти (словарь)
- Одна универсальная роль
- Трехслойная архитектура
- Локальный запуск через Makefile
- Минимальное тестирование

### Следующие шаги

1. ✅ Изучить vision.md
2. 🔄 Создать структуру проекта
3. 🔄 Реализовать MVP
4. 🔄 Протестировать
5. 🔄 Итерировать

### Связанные документы

- [idea.md](idea.md) — Исходная идея
- [ADR-01](adrs/ADR-01.md) — Выбор OpenAI
- [ADR-02](adrs/ADR-02.md) — Выбор aiogram
- [README.md](../README.md) — Инструкция

---

**Дата:** 2025-10-10  
**Версия:** 1.0 (MVP)
