# Getting Started

**Цель:** За 5 минут от клонирования до работающего бота.

---

## Требования

- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** — современный менеджер пакетов Python
- **Telegram Bot Token** — от [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** — от [platform.openai.com](https://platform.openai.com) или [OpenRouter](https://openrouter.ai)

---

## Установка за 3 шага

### 1. Клонировать и установить зависимости

```bash
git clone https://github.com/hanafubuuki/systtechbot.git
cd systtechbot
make install
```

Команда `make install` выполнит:
- `uv venv` — создаст виртуальное окружение
- `uv sync` — установит зависимости из `pyproject.toml`
- Создаст `.env` из `.env.example`

### 2. Настроить токены

Отредактируйте `.env` файл:

```ini
# Обязательные параметры
TELEGRAM_TOKEN=123456:ABC-DEF...          # От @BotFather
OPENAI_API_KEY=sk-proj-xxx...             # От OpenAI или OpenRouter

# Опциональные (для OpenRouter)
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-oss-20b:free
```

**Где получить токены:**

| Токен | Источник | Инструкция |
|-------|----------|------------|
| `TELEGRAM_TOKEN` | [@BotFather](https://t.me/BotFather) | Отправь `/newbot`, следуй инструкциям |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | API Keys → Create key |

### 3. Запустить бота

```bash
make run
```

Вы увидите:
```
INFO - __main__ - 🚀 Bot starting...
INFO - __main__ - ✅ Bot started successfully
```

---

## Первая проверка

Откройте бота в Telegram и попробуйте:

```
/start          → Приветствие
Привет!         → Ответ от AI
Как дела?       → Диалог с контекстом
/clear          → Очистка истории
/help           → Справка по командам
```

**Ожидаемо:** Бот отвечает на все сообщения, помнит контекст диалога.

---

## Если что-то не работает

### Ошибка: "TELEGRAM_TOKEN не установлен"
**Причина:** Отсутствует токен в `.env`
**Решение:** Проверьте `.env` файл, добавьте корректный токен

### Ошибка: "Configuration error: OPENAI_API_KEY"
**Причина:** Отсутствует API ключ
**Решение:** Добавьте `OPENAI_API_KEY` в `.env`

### Бот не отвечает в Telegram
**Причина:** Бот не запущен или токен неверный
**Решение:**
1. Проверьте, что `make run` показывает "Bot started successfully"
2. Проверьте токен через @BotFather → `/mybots` → выберите бота → API Token

### Бот отвечает "❌ Не удалось подключиться к сервису"
**Причина:** Проблема с OpenAI API
**Решение:**
1. Проверьте `OPENAI_API_KEY` корректный
2. Проверьте интернет-соединение
3. Для OpenRouter: проверьте `OPENAI_BASE_URL`

---

## Полезные команды

```bash
make run        # Запустить бота
make test       # Запустить тесты
make quality    # Проверить качество кода
make clean      # Очистить временные файлы
```

Логи сохраняются в `bot.log`.

---

## Следующие шаги

- 📐 [Архитектура](02-ARCHITECTURE.md) — понять как устроена система
- 📊 [Модель данных](03-DATA_MODEL.md) — работа со структурами данных
- 🛠️ [Разработка](04-DEVELOPMENT.md) — как вносить изменения

---

**Время прохождения:** ~5 минут
**Статус:** Готов к использованию ✅

