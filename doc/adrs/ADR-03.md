# ADR-03: Выбор PostgreSQL + Alembic + Raw SQL для персистентного хранения

**Статус:** Принято

**Дата:** 2025-10-16

**Контекст:** Sprint S1 - Реализация персистентного хранения истории диалогов

## Контекст и проблема

В текущей реализации (Sprint S0) контекст диалогов хранится in-memory в глобальном словаре Python. Это приводит к следующим проблемам:
- История диалогов теряется при перезапуске бота
- Невозможность масштабирования (несколько инстансов бота)
- Отсутствие аналитики и истории взаимодействий
- Ограничение по памяти при большом количестве пользователей

Требуется реализовать персистентное хранение с минимальной сложностью (KISS), сохраняя при этом:
- Soft delete стратегию (не удаляем данные физически)
- Tracking даты создания и длины сообщений
- Простоту разработки и поддержки

## Рассмотренные варианты

### База данных

1. **SQLite** - файловая БД
2. **PostgreSQL** - серверная реляционная БД
3. **MongoDB** - документная NoSQL БД
4. **Redis** - key-value хранилище

### Система миграций

1. **Alembic** - стандартный инструмент для SQLAlchemy
2. **Custom SQL migrations** - собственная система версионирования
3. **Django migrations** - миграции из Django ORM
4. **Yoyo migrations** - легковесный инструмент

### Подход к доступу к данным

1. **Raw SQL** - прямые SQL запросы
2. **SQLAlchemy ORM** - полноценный ORM
3. **SQLAlchemy Core** - SQL Expression Language
4. **asyncpg/psycopg** - драйвера с хелперами

## Решение

**База данных:** PostgreSQL 16
**Миграции:** Alembic
**Доступ к данным:** Raw SQL через psycopg3 (async)

## Обоснование

### Почему PostgreSQL vs SQLite?

**Преимущества PostgreSQL:**
- ✅ Production-ready: реальная серверная СУБД, готовая к production
- ✅ Масштабирование: поддержка нескольких подключений, connection pooling
- ✅ Типы данных: богатый набор типов (JSONB, Arrays, UUID и т.д.)
- ✅ Индексы: мощная система индексов (B-tree, GIN, GiST)
- ✅ Транзакции: полная поддержка ACID
- ✅ Экосистема: огромное сообщество, множество инструментов
- ✅ Будущее: возможность роста без миграции БД

**Недостатки SQLite для нашего случая:**
- ❌ Блокировки: проблемы при параллельных записях
- ❌ Ограничения типов: меньше возможностей для оптимизации
- ❌ Production: не рекомендуется для серверных приложений с конкурентным доступом

**Вывод:** PostgreSQL лучше подходит для Telegram бота, даже на этапе MVP. Docker упрощает развертывание до одной команды.

### Почему Alembic vs Custom migrations?

**Преимущества Alembic:**
- ✅ Стандарт индустрии: де-факто стандарт для Python-проектов
- ✅ Автоматическая генерация: может генерировать миграции из моделей
- ✅ История версий: четкая система версионирования
- ✅ Откаты: простой downgrade до любой версии
- ✅ Тестирование: проверенное временем решение
- ✅ Документация: отличная документация и примеры

**Недостатки Custom migrations:**
- ❌ Reinventing the wheel: нужно написать систему версионирования
- ❌ Больше кода: дополнительная поддержка собственной системы
- ❌ Багов больше: собственные решения обычно содержат больше багов
- ❌ Onboarding: новые разработчики должны изучать custom систему

**Вывод:** Alembic — проверенное решение, KISS подразумевает использование стандартных инструментов вместо написания собственных.

### Почему Raw SQL vs ORM?

**Преимущества Raw SQL:**
- ✅ Простота: никакой магии, явный контроль над запросами
- ✅ Производительность: полный контроль, оптимизация на уровне SQL
- ✅ Прозрачность: видно что происходит в БД
- ✅ Debugging: легко копировать запросы в psql для отладки
- ✅ KISS: нет абстракций, меньше слоев
- ✅ Меньше зависимостей: только драйвер psycopg

**Недостатки ORM для нашего случая:**
- ❌ Оверинжиниринг: для простых CRUD операций ORM избыточен
- ❌ Магия: неявное поведение, N+1 проблемы
- ❌ Сложность: дополнительный слой абстракции
- ❌ Размер: больше зависимостей (SQLAlchemy Core + ORM)

**Компромисс:** Используем Alembic для миграций (он работает и без ORM), но пишем Raw SQL для доступа к данным.

## Технические решения

### 1. Схема базы данных

```sql
-- Три таблицы для KISS подхода
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL UNIQUE,
    first_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP  -- soft delete
);

CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    telegram_chat_id BIGINT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP  -- soft delete
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    chat_id INTEGER NOT NULL REFERENCES chats(id),
    role VARCHAR(20) NOT NULL,  -- 'system', 'user', 'assistant'
    content TEXT NOT NULL,
    length INTEGER NOT NULL,     -- длина content в символах
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP         -- soft delete
);

-- Индекс для быстрого получения сообщений
CREATE INDEX idx_messages_user_chat
ON messages(user_id, chat_id, deleted_at, created_at);
```

**Особенности:**
- Нормализация: users и chats в отдельных таблицах (можно добавить метаданные позже)
- Soft delete: `deleted_at` для всех таблиц
- Tracking: `created_at` и `length` для каждого сообщения
- Индекс: оптимизация запроса истории диалога

### 2. Alembic конфигурация

```python
# alembic/env.py
from config import load_config

config = load_config()
context.config.set_main_option("sqlalchemy.url", config.database_url)
```

Миграции пишем вручную с Raw SQL:
```python
def upgrade():
    op.execute("""
        CREATE TABLE users (...)
    """)

def downgrade():
    op.execute("""
        DROP TABLE users CASCADE
    """)
```

### 3. Data Access Layer (services/database.py)

```python
import psycopg
from psycopg.rows import dict_row

# Singleton connection pool
_pool = None

async def get_connection():
    """Получить connection из пула"""
    global _pool
    if _pool is None:
        config = load_config()
        _pool = await psycopg.AsyncConnectionPool(
            config.database_url,
            min_size=1,
            max_size=10
        )
    return _pool.connection()

async def get_or_create_user(telegram_user_id: int, first_name: str) -> int:
    """Получить или создать пользователя"""
    async with await get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO users (telegram_user_id, first_name)
                VALUES (%s, %s)
                ON CONFLICT (telegram_user_id)
                DO UPDATE SET first_name = EXCLUDED.first_name
                RETURNING id
                """,
                (telegram_user_id, first_name)
            )
            result = await cur.fetchone()
            return result['id']
```

**Особенности:**
- Async поддержка через psycopg3
- Connection pooling для производительности
- Prepared statements (защита от SQL injection)
- dict_row для удобной работы с результатами

### 4. Docker развертывание

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: systtechbot
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: systtechbot
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Последствия

### Положительные

- ✅ **Персистентность:** История диалогов сохраняется между перезапусками
- ✅ **Production-ready:** PostgreSQL готов к production использованию
- ✅ **Масштабируемость:** Можно запускать несколько инстансов бота
- ✅ **Аналитика:** Возможность анализа истории взаимодействий
- ✅ **Простота кода:** Raw SQL прозрачен и понятен
- ✅ **Стандартные инструменты:** Alembic — де-факто стандарт
- ✅ **Быстрое развертывание:** Docker Compose — одна команда

### Отрицательные

- ❌ **Зависимость от PostgreSQL:** Нужен запущенный сервер БД
- ❌ **Сложность для новичков:** Требуется понимание SQL
- ❌ **Дополнительный сервис:** PostgreSQL в Docker
- ❌ **Ручное написание SQL:** Больше кода для CRUD операций

### Риски и митигация

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Ошибки в SQL запросах | Средняя | Unit тесты, integration тесты, code review |
| SQL injection | Низкая | Prepared statements, параметризованные запросы |
| Падение PostgreSQL | Низкая | Health checks, автоматический restart в Docker |
| Проблемы с миграциями | Средняя | Тестирование upgrade/downgrade, версионирование |

## Альтернативные пути

В будущем возможно:
- **Добавить SQLAlchemy Core** (без ORM) для более сложных запросов
- **Репликация** PostgreSQL для высокой доступности
- **Партиционирование** таблицы messages по дате
- **Кэширование** через Redis для горячих данных
- **Миграция на облачные БД** (AWS RDS, Yandex Managed PostgreSQL)

## Критерии пересмотра решения

Решение должно быть пересмотрено если:
- Производительность PostgreSQL становится узким местом (> 1000 req/s)
- Появляются сложные запросы, где ORM упростит код
- Требуется полностью offline решение (SQLite может быть лучше)
- Появляются требования к документным данным (MongoDB может быть лучше)

## Связанные решения

- ADR-01: Выбор OpenAI в качестве LLM-провайдера
- ADR-02: Выбор aiogram в качестве фреймворка для Telegram-бота
- [Будущее] ADR-04: Архитектура системы промптов

## Ссылки

- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Psycopg 3 Documentation](https://www.psycopg.org/psycopg3/)
- [Docker PostgreSQL Image](https://hub.docker.com/_/postgres)

---

**Версия:** 1.0
**Автор:** systtechbot team
**Sprint:** S1 - Персистентное хранение данных

