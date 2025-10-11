# План технического долга systtechbot

**Базовые документы:** [vision.md](vision.md) | [conventions.mdc](../.cursor/rules/conventions.mdc) | [workflow.mdc](../.cursor/rules/workflow.mdc)  
**Принцип:** Улучшение качества кода итерациями с сохранением работоспособности

**Основание:** Code review от Senior Python Tech Lead (2025-10-11)

---

## 📊 Отчет по прогрессу

| Итерация | Название | Статус | Задачи | Тестируемость | Дата |
|----------|----------|--------|--------|---------------|------|
| 0 | Инструменты качества | ✅ Завершено | 4/4 | `make quality` работает | 2025-10-11 |
| 1 | Критичный рефакторинг | ✅ Завершено | 5/5 | Тесты проходят | 2025-10-11 |
| 2 | Типизация | ✅ Завершено | 4/4 | `mypy` без ошибок | 2025-10-11 |
| 3 | Расширение тестов | ⏳ Ожидание | 0/5 | Coverage 80%+ | - |
| 4 | Финальная полировка | ⏳ Ожидание | 0/4 | Все проверки зеленые | - |

**Легенда:** ⏳ Ожидание | 🔄 В работе | ✅ Завершено | ❌ Заблокировано

**Прогресс:** 13/22 задач (59%)

---

## Итерация 0: Инструменты качества кода

**Цель:** Настроить автоматизированные инструменты для контроля качества  
**Тестируемость:** `make quality` запускается без ошибок

### Задачи

- [x] Добавить `ruff` (форматтер + линтер) в `pyproject.toml`
- [x] Добавить `mypy` (type checker) в `pyproject.toml`
- [x] Добавить `pytest-cov` для coverage в `pyproject.toml`
- [x] Создать команды в `Makefile`: `format`, `lint`, `typecheck`, `quality`

### Конфигурация

**pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
exclude = ["tests/"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Makefile (дополнить):**
```makefile
format:
	@echo "🎨 Форматирование кода..."
	uv run ruff format .
	@echo "✅ Форматирование завершено"

lint:
	@echo "🔍 Проверка линтером..."
	uv run ruff check .
	@echo "✅ Линтер завершен"

typecheck:
	@echo "🔎 Проверка типов..."
	uv run mypy bot.py handlers/ services/ roles/ config.py
	@echo "✅ Проверка типов завершена"

coverage:
	@echo "📊 Запуск тестов с покрытием..."
	uv run pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report: htmlcov/index.html"

quality: format lint typecheck test
	@echo "✅ Все проверки качества пройдены!"
```

### Проверка соответствия

- [ ] **conventions.mdc:** Код следует KISS (простые инструменты)
- [ ] **vision.md:** Без сложных паттернов, только необходимое
- [ ] **workflow.mdc:** Изменения согласованы, протестированы

### Тест

```bash
# 1. Установить новые зависимости
uv sync

# 2. Запустить форматирование
make format

# 3. Запустить линтер
make lint

# 4. Запустить type checker
make typecheck

# 5. Полная проверка
make quality

# Ожидаемо: все команды выполняются без критичных ошибок
```

---

## Итерация 1: Критичный рефакторинг

**Цель:** Исправить критичные проблемы архитектуры  
**Тестируемость:** Все тесты проходят, бот работает

### Задачи

- [x] Убрать глобальную загрузку config в `handlers/messages.py:15`
- [x] Реализовать singleton/кэширование для OpenAI клиента в `services/llm.py`
- [x] Создать `constants.py` с enum `MessageRole` вместо magic strings
- [x] Обновить все места использования с проверкой работоспособности
- [x] Обновить `conventions.mdc` и `vision.md` на соответствие изменениям

### Детали реализации

**1. constants.py (новый файл):**
```python
"""Константы приложения"""
from enum import Enum


class MessageRole(str, Enum):
    """Роли сообщений в диалоге"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
```

**2. services/llm.py (рефакторинг):**
```python
# Кэш клиентов OpenAI
_client_cache: dict[tuple[str, str], AsyncOpenAI] = {}


def _get_or_create_client(config: Config) -> AsyncOpenAI:
    """Получить или создать клиента OpenAI (singleton pattern)"""
    key = (config.openai_api_key, config.openai_base_url)
    if key not in _client_cache:
        _client_cache[key] = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
    return _client_cache[key]


async def get_llm_response(messages: list, config: Config) -> str:
    client = _get_or_create_client(config)
    # ... остальной код
```

**3. handlers/messages.py (убрать глобальный config):**
```python
# ❌ Убрать строку 14-15:
# config = load_config()

# ✅ Загружать внутри функции:
@router.message()
async def handle_message(message: Message):
    config = load_config()  # Загружаем здесь
    # ... остальной код
```

**4. Использование MessageRole:**
```python
# services/context.py
from constants import MessageRole

# ❌ Было:
if messages[0]["role"] == "system":

# ✅ Стало:
if messages[0]["role"] == MessageRole.SYSTEM:
```

### Проверка соответствия

- [ ] **conventions.mdc:** Нет глобальных side effects, singleton простой
- [ ] **vision.md:** Сохранена простота, нет overengineering
- [ ] **workflow.mdc:** Код согласован, покрыт тестами

### Тест

```bash
# 1. Запустить тесты
make test

# 2. Запустить бота
make run

# 3. Проверить в Telegram:
#    - /start
#    - Несколько сообщений подряд
#    - /clear
#    - Еще сообщения

# 4. Проверить качество
make quality

# Ожидаемо: все работает как раньше + никаких предупреждений
```

---

## Итерация 2: Строгая типизация

**Цель:** Добавить type hints везде, пройти mypy без ошибок  
**Тестируемость:** `mypy` проходит с 0 ошибками

### Задачи

- [x] Добавить type hints во все публичные функции (если отсутствуют)
- [x] Добавить аннотации для переменных где неоднозначно
- [x] Исправить все ошибки mypy
- [x] Создать типы для словарей (TypedDict для context)
- [x] Обновить `conventions.mdc` и `vision.md` на соответствие изменениям

### Детали реализации

**1. services/context.py - TypedDict для контекста:**
```python
from typing import TypedDict
from datetime import datetime


class Message(TypedDict):
    """Структура сообщения"""
    role: str
    content: str


class UserContext(TypedDict):
    """Структура контекста пользователя"""
    messages: list[Message]
    user_name: str | None
    last_activity: datetime


# Типизация глобального хранилища
user_contexts: dict[tuple[int, int], UserContext] = {}


def get_context(user_id: int, chat_id: int) -> UserContext:
    """Получить контекст пользователя"""
    key = (user_id, chat_id)
    if key in user_contexts:
        return user_contexts[key]
    return {"messages": [], "user_name": None, "last_activity": datetime.now()}
```

**2. bot.py - аннотации:**
```python
from typing import NoReturn


async def main() -> None:
    """Главная функция запуска бота"""
    # ... код
```

**3. handlers/messages.py:**
```python
from aiogram.types import Message


@router.message()
async def handle_message(message: Message) -> None:
    """Обработчик всех текстовых сообщений"""
    # ... код
```

### Проверка соответствия

- [ ] **conventions.mdc:** Type hints обязательны для публичных функций
- [ ] **vision.md:** Простота сохранена, нет сложных типов
- [ ] **workflow.mdc:** Изменения протестированы

### Тест

```bash
# 1. Проверить типы
make typecheck

# 2. Запустить тесты
make test

# 3. Полная проверка
make quality

# Ожидаемо: mypy не находит ошибок (0 errors)
```

---

## Итерация 3: Расширение тестового покрытия

**Цель:** Довести coverage до 80%+  
**Тестируемость:** `make coverage` показывает 80%+ покрытие

### Задачи

- [ ] Создать `tests/test_llm.py` с мокированием OpenAI
- [ ] Создать `tests/test_handlers.py` для интеграционных тестов
- [ ] Добавить parametrized тесты для `trim_context`
- [ ] Создать `tests/test_config.py` для валидации конфигурации
- [ ] Обновить `conventions.mdc` и `vision.md` на соответствие изменениям

### Файлы тестов

**tests/test_llm.py:**
```python
"""Тесты для сервиса LLM"""
import pytest
from unittest.mock import AsyncMock, patch
from services.llm import get_llm_response, _get_or_create_client
from config import Config


@pytest.fixture
def mock_config():
    """Фикстура с тестовой конфигурацией"""
    return Config(
        telegram_token="test_token",
        openai_api_key="test_key",
        openai_base_url="https://api.test.com",
        openai_model="gpt-test"
    )


@pytest.mark.asyncio
async def test_llm_response_success(mock_config):
    """Тест успешного ответа от LLM"""
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content="Test response"))
    ]
    
    with patch("services.llm.AsyncOpenAI") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        result = await get_llm_response(
            [{"role": "user", "content": "Hi"}], 
            mock_config
        )
        
        assert result == "Test response"


@pytest.mark.asyncio
async def test_llm_response_empty(mock_config):
    """Тест пустого ответа от LLM"""
    mock_response = AsyncMock()
    mock_response.choices = []
    
    with patch("services.llm.AsyncOpenAI") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        result = await get_llm_response(
            [{"role": "user", "content": "Hi"}], 
            mock_config
        )
        
        assert "пустой ответ" in result.lower()


@pytest.mark.asyncio
async def test_llm_markdown_cleanup(mock_config):
    """Тест очистки markdown форматирования"""
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content="**Bold** and *italic* text"))
    ]
    
    with patch("services.llm.AsyncOpenAI") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        result = await get_llm_response(
            [{"role": "user", "content": "Hi"}], 
            mock_config
        )
        
        assert "**" not in result
        assert "*" not in result
```

**tests/test_config.py:**
```python
"""Тесты для конфигурации"""
import pytest
from unittest.mock import patch
from config import load_config


def test_load_config_missing_telegram_token():
    """Тест ошибки при отсутствии TELEGRAM_TOKEN"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}, clear=True):
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN"):
            load_config()


def test_load_config_missing_openai_key():
    """Тест ошибки при отсутствии OPENAI_API_KEY"""
    with patch.dict("os.environ", {"TELEGRAM_TOKEN": "test"}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            load_config()


def test_load_config_defaults():
    """Тест дефолтных значений"""
    with patch.dict("os.environ", {
        "TELEGRAM_TOKEN": "test_token",
        "OPENAI_API_KEY": "test_key"
    }):
        config = load_config()
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.max_context_messages == 10
```

**tests/test_context.py (дополнить):**
```python
@pytest.mark.parametrize("input_len,max_messages,expected_len", [
    (5, 10, 5),      # меньше лимита
    (11, 10, 11),    # ровно лимит (system + 10)
    (25, 10, 11),    # больше лимита
    (1, 10, 1),      # один system
])
def test_trim_context_parametrized(input_len, max_messages, expected_len):
    """Параметризованный тест усечения контекста"""
    messages = [
        {"role": "system", "content": "System"},
        *[{"role": "user", "content": f"msg{i}"} for i in range(input_len - 1)]
    ]
    result = trim_context(messages, max_messages)
    assert len(result) == expected_len
    if result:
        assert result[0]["role"] == "system"
```

### Проверка соответствия

- [ ] **conventions.mdc:** Тестируем критичное, не тривиальное
- [ ] **vision.md:** Минимальное тестирование, но достаточное
- [ ] **workflow.mdc:** Тесты зеленые перед коммитом

### Тест

```bash
# 1. Запустить с покрытием
make coverage

# 2. Открыть HTML отчет
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html

# 3. Проверить метрики
# Ожидаемо: Coverage >= 80%
# Все критичные модули покрыты
```

---

## Итерация 4: Финальная полировка

**Цель:** Привести код в идеальное состояние  
**Тестируемость:** Все проверки `make quality` проходят

### Задачи

- [ ] Пройти по всем файлам с `make format` и `make lint`
- [ ] Добавить docstrings где отсутствуют (Google style)
- [ ] Обновить README.md с новыми командами
- [ ] Финальная проверка и обновление `conventions.mdc` и `vision.md`

### Обновления

**README.md (дополнить раздел):**
```markdown
## 🔍 Контроль качества

### Команды

```bash
make format     # Форматирование кода (ruff)
make lint       # Проверка линтером (ruff)
make typecheck  # Проверка типов (mypy)
make coverage   # Тесты с покрытием
make quality    # Полная проверка качества
```

### Метрики качества

- ✅ Форматирование: ruff
- ✅ Линтер: ruff (E, W, F, I, B, C4, UP)
- ✅ Типизация: mypy (strict mode)
- ✅ Coverage: 80%+
- ✅ Все тесты: зеленые
```

**Docstrings (Google style):**
```python
def trim_context(messages: list, max_messages: int = 10) -> list:
    """Усечь контекст до максимального количества сообщений.
    
    Всегда сохраняет system prompt (первое сообщение).
    
    Args:
        messages: Список сообщений в формате OpenAI
        max_messages: Максимальное количество сообщений (не считая system)
        
    Returns:
        Усеченный список сообщений с сохранением system prompt
        
    Example:
        >>> msgs = [{"role": "system", ...}, {"role": "user", ...}, ...]
        >>> trim_context(msgs, max_messages=5)
        [system_msg, last_5_msgs]
    """
```

### Проверка соответствия

#### conventions.mdc checklist:
- [ ] Код следует KISS принципу
- [ ] Нет дублирования из vision.md
- [ ] Обработка ошибок везде
- [ ] Логирование структурировано
- [ ] Type hints для публичных функций
- [ ] Нет "умного" кода
- [ ] Все файлы < 200 строк

#### vision.md checklist:
- [ ] Python 3.11+
- [ ] Зависимости только из разрешенного списка
- [ ] In-memory хранение
- [ ] Трехслойная архитектура сохранена
- [ ] KISS, YAGNI, MVP-first
- [ ] Fail Fast при ошибках

### Тест

```bash
# 1. Полная проверка качества
make quality

# 2. Визуальная проверка покрытия
make coverage

# 3. Запуск бота
make run

# 4. Smoke test в Telegram:
#    - /start
#    - Диалог с историей (5+ сообщений)
#    - /clear
#    - /help
#    - Проверка при отключенном интернете

# Ожидаемо:
# ✅ make quality - все зеленое
# ✅ Coverage >= 80%
# ✅ Бот работает стабильно
# ✅ Код соответствует всем conventions
```

---

## 📋 Checklist финального качества

### Автоматические проверки
- [ ] `make format` - без изменений
- [ ] `make lint` - 0 ошибок
- [ ] `make typecheck` - 0 ошибок mypy
- [ ] `make test` - все тесты зеленые
- [ ] `make coverage` - >= 80%

### Соответствие документам
- [ ] **conventions.mdc:** все пункты соблюдены
- [ ] **vision.md:** архитектура и принципы не нарушены
- [ ] **workflow.mdc:** процесс разработки соблюден

### Ручные проверки
- [ ] README.md актуален
- [ ] Все файлы имеют docstrings
- [ ] Логи читаемы и структурированы
- [ ] Бот работает стабильно в Telegram
- [ ] Нет технического долга

---

## 🎯 Команды для работы

```bash
# Установка новых зависимостей
uv sync

# Разработка
make format      # Перед коммитом
make quality     # Полная проверка

# Тестирование
make test        # Быстрые тесты
make coverage    # С отчетом покрытия

# Запуск
make run         # Запустить бота
```

---

## 📊 Ожидаемые результаты

После завершения всех итераций:

1. **Качество кода**
   - Автоформатирование (ruff)
   - Линтинг без ошибок
   - Строгая типизация (mypy)
   - Coverage 80%+

2. **Архитектура**
   - Нет глобальных side effects
   - Singleton для OpenAI клиента
   - Константы вместо magic strings
   - Type safety везде

3. **Тестирование**
   - Unit тесты для всех сервисов
   - Интеграционные тесты для handlers
   - Parametrized тесты
   - Мокирование внешних API

4. **Документация**
   - Актуальный README
   - Docstrings везде
   - Примеры использования

5. **Developer Experience**
   - `make quality` - одна команда для всего
   - Быстрая обратная связь
   - Понятные ошибки

---

**Версия:** 1.0  
**Дата создания:** 2025-10-11  
**Основание:** Code review (Senior Python Tech Lead)  
**Связанные документы:** [vision.md](vision.md) | [tasklist.md](tasklist.md) | [conventions.mdc](../.cursor/rules/conventions.mdc)

