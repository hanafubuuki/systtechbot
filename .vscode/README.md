# 🎯 Конфигурация Cursor/VS Code для systtechbot

Этот каталог содержит настройки для запуска и отладки проекта через UI Cursor/VS Code.

---

## 📋 Файлы конфигурации

### `tasks.json` — Задачи (Tasks)

Быстрые команды для типичных операций:

**Запуск:**
- 🚀 **Run Bot** — запустить бота
- 🧪 **Run All Tests** — все тесты
- 🧪 **Run Tests with Coverage** — тесты с отчетом покрытия
- 🧪 **Run Current Test File** — запустить текущий файл с тестами

**Проверка качества:**
- 🎨 **Format Code** — форматирование (ruff)
- 🔍 **Lint Code** — проверка линтером (ruff)
- 🔎 **Check Types** — проверка типов (mypy)
- ✅ **Quality Check (All)** — все проверки последовательно

**Утилиты:**
- 🧹 **Clean** — очистка временных файлов
- 📦 **Install Dependencies** — установка зависимостей
- 📊 **Open Coverage Report** — открыть HTML отчет покрытия

**Как использовать:**
1. Нажми `Ctrl+Shift+P` (или `Cmd+Shift+P` на Mac)
2. Введи "Tasks: Run Task"
3. Выбери нужную задачу

Или:
- `Ctrl+Shift+B` — запустить задачу по умолчанию (Run All Tests)

---

### `launch.json` — Запуск и отладка

Конфигурации для запуска с отладкой:

**Основные:**
- 🚀 **Run Bot** — запуск бота (с форматированием перед стартом)
- 🐛 **Debug Bot** — запуск бота с отладкой

**Тестирование:**
- 🧪 **Debug Current Test File** — отладка текущего файла
- 🧪 **Debug All Tests** — отладка всех тестов
- 🧪 **Debug Test with Coverage** — отладка с покрытием
- 🧪 **Debug Specific Test** — отладка конкретной функции теста

**Как использовать:**
1. Открой файл, который хочешь запустить/отладить
2. Нажми `F5` или иконку "Run and Debug" на боковой панели
3. Выбери конфигурацию
4. Устанавливай breakpoints кликом слева от номеров строк

**Горячие клавиши отладки:**
- `F5` — запустить/продолжить
- `F9` — установить/снять breakpoint
- `F10` — шаг с обходом (step over)
- `F11` — шаг с заходом (step into)
- `Shift+F11` — шаг с выходом (step out)
- `Shift+F5` — остановить отладку

---

### `settings.json` — Настройки проекта

Автоматические настройки для:

**Python:**
- Путь к интерпретатору (.venv)
- Автоактивация виртуального окружения

**Тестирование:**
- pytest включен по умолчанию
- Автообнаружение тестов при сохранении

**Форматирование:**
- Ruff как formatter
- Форматирование при сохранении
- Автоорганизация импортов

**Линтинг:**
- mypy включен (strict mode)
- ruff включен

**Редактор:**
- Линия на 100 символов
- Табы = 4 пробела
- Удаление пробелов в конце строк

---

### `extensions.json` — Рекомендуемые расширения

При открытии проекта Cursor предложит установить:

**Обязательные:**
- Python (Microsoft)
- Ruff (Formatter + Linter)
- mypy Type Checker

**Рекомендуемые:**
- Coverage Gutters (отображение покрытия)
- GitLens (улучшенный Git)
- Markdown All in One
- Todo Tree

**Как установить:**
- Cursor покажет уведомление "Install recommended extensions"
- Или: `Ctrl+Shift+P` → "Extensions: Show Recommended Extensions"

---

## 🚀 Быстрый старт

### 1. Открой проект в Cursor

```bash
cd c:\zz\systtechbot
cursor .
```

### 2. Установи зависимости

- Нажми `Ctrl+Shift+P`
- Введи "Tasks: Run Task"
- Выбери "📦 Install Dependencies"

Или в терминале:
```bash
uv sync
```

### 3. Запусти бота

**Вариант 1: Через Task**
- `Ctrl+Shift+P` → "Tasks: Run Task" → "🚀 Run Bot"

**Вариант 2: С отладкой**
- `F5` → выбери "🚀 Run Bot"

**Вариант 3: В терминале**
```bash
uv run bot.py
```

### 4. Запусти тесты

**Вариант 1: Через UI**
- Открой боковую панель "Testing" (колбочка)
- Нажми "Run All Tests"

**Вариант 2: Через Task**
- `Ctrl+Shift+B` (default task)

**Вариант 3: С coverage**
- `Ctrl+Shift+P` → "Tasks: Run Task" → "🧪 Run Tests with Coverage"

---

## 🎯 Типичные сценарии

### Сценарий 1: Добавил новую функцию

1. Напиши код
2. Сохрани (Ctrl+S) — автоматически форматируется
3. Напиши тесты
4. Запусти тесты текущего файла: `Ctrl+Shift+P` → "Tasks: Run Task" → "🧪 Run Current Test File"
5. Если нужна отладка: `F5` → "🧪 Debug Current Test File"

### Сценарий 2: Перед коммитом

1. Запусти полную проверку качества:
   - `Ctrl+Shift+P` → "Tasks: Run Task" → "✅ Quality Check (All)"
2. Проверь coverage:
   - `Ctrl+Shift+P` → "Tasks: Run Task" → "📊 Open Coverage Report"
3. Убедись, что все зеленое ✅

### Сценарий 3: Отладка сложного бага

1. Открой файл с проблемой
2. Установи breakpoints (клик слева от номера строки)
3. Нажми `F5` → выбери конфигурацию
4. Используй:
   - `F10` — следующая строка
   - `F11` — зайти в функцию
   - Hover над переменными для просмотра значений
   - Watch панель для отслеживания выражений

### Сценарий 4: Проверка покрытия кода

1. Запусти тесты с coverage
2. Открой HTML отчет: "📊 Open Coverage Report"
3. Или установи "Coverage Gutters":
   - Зеленые линии = покрыты
   - Красные линии = не покрыты
   - Серые линии = не исполняемые

---

## ⚙️ Настройка под себя

### Изменить горячие клавиши

1. `Ctrl+Shift+P` → "Preferences: Open Keyboard Shortcuts"
2. Найди нужную команду
3. Назначь свою комбинацию

### Добавить свою задачу

Отредактируй `tasks.json`:
```json
{
  "label": "Моя задача",
  "type": "shell",
  "command": "uv",
  "args": ["run", "python", "my_script.py"]
}
```

### Отключить форматирование при сохранении

В `settings.json`:
```json
"[python]": {
  "editor.formatOnSave": false
}
```

---

## 🐛 Troubleshooting

### Проблема: Python не найден

**Решение:**
1. Убедись, что `.venv` создан: `uv venv`
2. Перезагрузи Cursor
3. Выбери интерпретатор: `Ctrl+Shift+P` → "Python: Select Interpreter"

### Проблема: Тесты не обнаруживаются

**Решение:**
1. Проверь `python.testing.pytestEnabled` в settings
2. Перезагрузи окно теста: `Ctrl+Shift+P` → "Testing: Refresh Tests"

### Проблема: ruff не работает

**Решение:**
1. Установи расширение: `charliermarsh.ruff`
2. Перезагрузи Cursor
3. Проверь, что `uv sync` выполнен

### Проблема: Coverage не отображается

**Решение:**
1. Запусти тесты с coverage
2. Установи "Coverage Gutters"
3. Нажми "Watch" внизу статус-бара

---

## 📚 Полезные ссылки

- [VS Code Python Guide](https://code.visualstudio.com/docs/python/python-tutorial)
- [VS Code Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

---

**Версия:** 1.0
**Дата:** 2025-10-11
**Совместимость:** Cursor, VS Code 1.80+

