# API для статистики диалогов systtechbot

Mock API для дашборда статистики диалогов Telegram-бота.

## Быстрый старт

### 1. Установка зависимостей

```bash
make api-install
```

### 2. Запуск Mock API

```bash
make api-run
```

API будет доступен по адресу: `http://localhost:8000`

### 3. Открытие документации

```bash
make api-docs
```

Или откройте в браузере: `http://localhost:8000/docs`

## Endpoints

### GET /api/v1/stats

Получить статистику для дашборда.

**Query параметры:**
- `period` (int, optional) - Период в днях для временного ряда. Допустимые значения: 7, 30, 90. По умолчанию: 90.

**Пример запроса:**
```bash
curl http://localhost:8000/api/v1/stats?period=30
```

**Пример ответа:**
```json
{
  "total_users": {
    "value": 1234,
    "change_percent": 12.5,
    "trend": "up"
  },
  "total_chats": {
    "value": 5678,
    "change_percent": -5.2,
    "trend": "down"
  },
  "total_messages": {
    "value": 89012,
    "change_percent": 8.7,
    "trend": "up"
  },
  "avg_message_length": {
    "value": 125.3,
    "change_percent": 0.5,
    "trend": "stable"
  },
  "activity_chart": [
    {
      "date": "2025-09-18",
      "messages": 142
    },
    ...
  ]
}
```

## Структура проекта

```
api/
├── __init__.py
├── main.py              # FastAPI приложение
├── models.py            # Pydantic модели
├── config.py            # Конфигурация
├── collectors/          # Коллекторы статистики
│   ├── base.py          # Абстрактный интерфейс
│   ├── mock.py          # Mock реализация
│   └── real.py          # Real реализация (S5)
└── tests/               # Тесты
    └── test_api.py
```

## Режимы работы

### Mock режим (по умолчанию)

Генерирует тестовые данные для разработки frontend.

```bash
# .env
API_MODE=mock
```

### Real режим (будет в S5)

Получает данные из реальной базы данных PostgreSQL.

```bash
# .env
API_MODE=real
```

## Конфигурация

Настройки через переменные окружения в `.env`:

```ini
# Режим работы API
API_MODE=mock           # mock или real

# Хост и порт
API_HOST=0.0.0.0
API_PORT=8000

# Mock seed (для воспроизводимости данных)
API_MOCK_SEED=42

# CORS origins (разделенные запятыми)
API_CORS_ORIGINS=*
```

## Тестирование

Запуск тестов:

```bash
make api-test
```

Запуск с покрытием:

```bash
uv run pytest api/tests/ -v --cov=api --cov-report=html
```

## Разработка

### Проверка качества кода

```bash
# Форматирование
uv run ruff format api/

# Линтинг
uv run ruff check api/

# Проверка типов
uv run mypy api/
```

### Модели данных

Все модели данных определены в `api/models.py` с использованием Pydantic.

**Основные модели:**
- `MetricCard` - Карточка метрики с трендом
- `TimeSeriesPoint` - Точка временного ряда
- `DashboardStats` - Полная статистика для дашборда

### Добавление нового коллектора

1. Создайте класс, наследующий `StatCollector`
2. Реализуйте метод `get_dashboard_stats()`
3. Зарегистрируйте в `api/collectors/__init__.py`

```python
from api.collectors.base import StatCollector
from api.models import DashboardStats

class MyCollector(StatCollector):
    async def get_dashboard_stats(self, period_days: int = 90) -> DashboardStats:
        # Ваша реализация
        ...
```

## Связанные документы

- [Функциональные требования к дашборду](../frontend/doc/dashboard-requirements.md)
- [Frontend Roadmap](../frontend/doc/frontend-roadmap.md)
- [План S1](../s1-mock-api-dashboard.plan.md)

## Лицензия

Внутренний проект systtechbot

