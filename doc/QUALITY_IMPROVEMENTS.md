# Улучшения качества кода systtechbot

**Дата:** 2025-10-11  
**Основание:** Code review от Senior Python Tech Lead

---

## 📋 Обновленные документы

### 1. ✅ Создан `workflow_tech_debt.mdc`
**Путь:** `.cursor/rules/workflow_tech_debt.mdc`

Специальный workflow для работы с техническим долгом:
- Фокус на качестве без ломающих изменений
- Обязательная проверка `make quality` на каждом этапе
- Специальный формат коммитов: `refactor(tech-debt-N): описание`
- Метрики качества в каждой итерации

### 2. ✅ Обновлен `conventions.mdc`
**Путь:** `.cursor/rules/conventions.mdc`  
**Версия:** 2.0

**Добавлены разделы:**

#### Форматирование кода
- Инструмент: `ruff`
- Длина строки: 100 символов
- Автоматическое форматирование: `make format`

#### Линтинг и анализ
- Инструмент: `ruff` (замена black + flake8 + isort)
- Правила: E, W, F, I, B, C4, UP
- Команда: `make lint`
- Цель: 0 ошибок

#### Проверка типов
- Инструмент: `mypy`
- Strict mode для всех публичных функций
- Современный синтаксис Python 3.11+ (list[str], str | None)
- Команда: `make typecheck`
- Цель: 0 ошибок

#### Документирование
- Google Style для docstrings
- Обязательны для всех публичных функций и классов
- Примеры использования в docstrings

#### Тестирование
- Целевой coverage: >= 80%
- Parametrized тесты
- Мокирование внешних вызовов
- Фикстуры для повторяющихся данных

#### Лучшие практики Python
- Современный синтаксис (Python 3.11+)
- Dataclasses для структур
- Context managers
- Enum вместо magic strings
- Нет изменяемых default arguments
- Правильная работа с async/await

#### Константы и Enums
- MessageRole enum вместо строк
- Константы для всех magic numbers
- Нет magic strings в коде

#### Полная проверка качества
- Команда: `make quality`
- Запускает: format → lint → typecheck → test
- Обязательна перед коммитом

### 3. ✅ Обновлен `vision.md`
**Путь:** `doc/vision.md`  
**Версия:** 1.1 (MVP + Quality)

**Изменения:**

#### Зависимости
Добавлены инструменты качества:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",      # Coverage reporting
    "ruff>=0.1.0",             # Formatter + linter
    "mypy>=1.7.0",             # Type checker
]
```

#### Новый раздел: Инструменты качества кода
- ruff — форматтер и линтер
- mypy — типизация
- pytest-cov — coverage
- Целевой coverage: >= 80%

#### Обновлен раздел: Тестирование
- Уровень: достаточный (было: минимальный)
- Интеграционные тесты
- Мокирование
- Parametrized тесты

#### Новый раздел: Качество кода
- Форматирование: `ruff format`
- Линтинг: `ruff check`
- Типизация: `mypy`
- Команда: `make quality`

#### Обновлен Makefile
Новые команды:
- `make format` — форматирование
- `make lint` — линтинг
- `make typecheck` — проверка типов
- `make coverage` — тесты с покрытием
- `make quality` — полная проверка

#### Критерии успеха MVP
Добавлены:
- ✅ Качество кода: `make quality` проходит без ошибок
- ✅ Покрытие тестами >= 80%

### 4. ✅ Создан `tasklist_tech_debt.md`
**Путь:** `doc/tasklist_tech_debt.md`

План работы по улучшению качества на 5 итераций:

| Итерация | Задачи | Цель |
|----------|--------|------|
| 0 | Инструменты качества | Настроить ruff, mypy, pytest-cov |
| 1 | Критичный рефакторинг | Убрать глобальные side effects, singleton OpenAI |
| 2 | Строгая типизация | Type hints везде, TypedDict, mypy 0 errors |
| 3 | Расширение тестов | Coverage 80%+, моки, parametrized |
| 4 | Финальная полировка | Docstrings, README, финальные проверки |

---

## 🎯 Новые команды

### Проверка качества
```bash
make format      # Форматирование кода (автоматически)
make lint        # Проверка линтером (0 ошибок)
make typecheck   # Проверка типов (0 ошибок mypy)
make coverage    # Тесты с отчетом о покрытии
make quality     # Полная проверка (все выше)
```

### Разработка
```bash
make install     # Установка зависимостей (включая dev)
make run         # Запуск бота
make test        # Быстрые тесты
make clean       # Очистка временных файлов
```

---

## 📊 Метрики качества

| Метрика | Инструмент | Целевое значение |
|---------|------------|------------------|
| Форматирование | ruff format | 100% (авто) |
| Стиль кода | ruff check | 0 ошибок |
| Типизация | mypy | 0 ошибок |
| Тесты | pytest | 100% passed |
| Покрытие | pytest-cov | >= 80% |

---

## 🚀 Как начать работу

### 1. Установка инструментов
```bash
cd systtechbot
uv sync  # Установит все dev зависимости
```

### 2. Первая проверка
```bash
make quality
```

**Ожидаемо:** Может показать ошибки — это нормально, мы их исправим в итерациях.

### 3. Начать работу по плану
См. `doc/tasklist_tech_debt.md` — Итерация 0

---

## 📚 Связанные документы

- [tasklist_tech_debt.md](tasklist_tech_debt.md) — Детальный план работ
- [workflow_tech_debt.mdc](../.cursor/rules/workflow_tech_debt.mdc) — Процесс работы
- [conventions.mdc](../.cursor/rules/conventions.mdc) — Соглашения (обновлено)
- [vision.md](vision.md) — Техническое видение (обновлено)

---

## ✅ Checklist до начала работы

- [ ] Прочитал обновленный `conventions.mdc`
- [ ] Прочитал `workflow_tech_debt.mdc`
- [ ] Прочитал `tasklist_tech_debt.md`
- [ ] Установил зависимости: `uv sync`
- [ ] Проверил текущее состояние: `make quality`
- [ ] Готов начать Итерацию 0

---

**Следующий шаг:** Начать работу с Итерации 0 из `tasklist_tech_debt.md`

