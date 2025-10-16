# База данных: Документация

## Обзор

Проект использует **PostgreSQL** для персистентного хранения истории диалогов. Решение следует принципу KISS (Keep It Simple, Stupid) и обеспечивает надежное сохранение данных между перезапусками бота.

**Ключевые принципы:**
- 🔄 **Soft delete** — данные не удаляются физически, только помечаются как удалённые
- 📊 **Метаданные сообщений** — дата создания и длина в символах
- 🎯 **Raw SQL** — прозрачный доступ к данным без "магии" ORM
- 🐳 **Docker Compose** — простое развёртывание локального окружения

**Архитектурное решение:** [ADR-03](../adrs/ADR-03.md) (выбор PostgreSQL, Alembic, Raw SQL)

---

## Схема базы данных

### Таблицы

#### `users`
Хранит информацию о пользователях Telegram.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL PRIMARY KEY | Внутренний ID пользователя |
| `telegram_user_id` | BIGINT NOT NULL UNIQUE | ID пользователя в Telegram |
| `first_name` | VARCHAR(255) | Имя пользователя |
| `created_at` | TIMESTAMP NOT NULL DEFAULT NOW() | Дата создания записи |
| `deleted_at` | TIMESTAMP | Дата "удаления" (soft delete) |

#### `chats`
Хранит информацию о чатах Telegram.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL PRIMARY KEY | Внутренний ID чата |
| `telegram_chat_id` | BIGINT NOT NULL UNIQUE | ID чата в Telegram |
| `created_at` | TIMESTAMP NOT NULL DEFAULT NOW() | Дата создания записи |
| `deleted_at` | TIMESTAMP | Дата "удаления" (soft delete) |

#### `messages`
Хранит сообщения диалогов.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL PRIMARY KEY | Внутренний ID сообщения |
| `user_id` | INTEGER NOT NULL | FK на `users.id` |
| `chat_id` | INTEGER NOT NULL | FK на `chats.id` |
| `role` | VARCHAR(20) NOT NULL | Роль: `system`, `user`, `assistant` |
| `content` | TEXT NOT NULL | Текст сообщения |
| `length` | INTEGER NOT NULL | Длина сообщения в символах |
| `created_at` | TIMESTAMP NOT NULL DEFAULT NOW() | Дата создания сообщения |
| `deleted_at` | TIMESTAMP | Дата "удаления" (soft delete) |

**Индексы:**
- `idx_messages_user_chat` на `(user_id, chat_id, deleted_at, created_at)` — для эффективного получения сообщений

### ER-диаграмма

```
┌──────────────────┐
│     users        │
├──────────────────┤
│ id (PK)          │
│ telegram_user_id │◄───────┐
│ first_name       │        │
│ created_at       │        │
│ deleted_at       │        │
└──────────────────┘        │
                            │
                            │ 1:N
                            │
┌──────────────────┐        │
│     chats        │        │
├──────────────────┤        │
│ id (PK)          │◄───┐   │
│ telegram_chat_id │    │   │
│ created_at       │    │   │
│ deleted_at       │    │   │
└──────────────────┘    │   │
                        │   │
                        │ 1:N
                        │   │
┌──────────────────┐    │   │
│    messages      │    │   │
├──────────────────┤    │   │
│ id (PK)          │    │   │
│ user_id (FK)     │────┼───┘
│ chat_id (FK)     │────┘
│ role             │
│ content          │
│ length           │
│ created_at       │
│ deleted_at       │
└──────────────────┘
```

---

## Локальное развёртывание

### 1. Запуск PostgreSQL

Через Docker Compose:
```bash
make db-up
```

Или вручную:
```bash
docker-compose up -d
```

### 2. Настройка .env

Добавьте в `.env` строку подключения к БД:
```ini
DATABASE_URL=postgresql://user:password@localhost:5432/systtechbot_db
```

### 3. Применение миграций

```bash
make db-migrate
```

Или вручную:
```bash
uv run alembic upgrade head
```

### 4. Проверка состояния БД

Подключитесь к БД через любой клиент (DBeaver, psql, pgAdmin):
```bash
psql postgresql://user:password@localhost:5432/systtechbot_db
```

Проверьте таблицы:
```sql
\dt
SELECT * FROM users;
SELECT * FROM chats;
SELECT * FROM messages;
```

---

## Миграции (Alembic)

### Создание новой миграции

```bash
uv run alembic revision -m "описание изменений"
```

### Применение миграций

```bash
uv run alembic upgrade head
```

### Откат миграций

```bash
# Откатить последнюю миграцию
uv run alembic downgrade -1

# Откатить все миграции
uv run alembic downgrade base
```

### История миграций

```bash
uv run alembic history
uv run alembic current
```

### Сброс БД

Для полного сброса и повторного применения миграций:
```bash
make db-reset
```

Или вручную:
```bash
docker-compose down -v
docker-compose up -d
# Подождите 5 секунд для готовности БД
uv run alembic upgrade head
```

---

## Слой доступа к данным (DAL)

Файл: `services/database.py`

### Архитектура

Используется паттерн **Data Access Layer (DAL)** с **raw SQL** для максимальной прозрачности и контроля.

**Ключевые компоненты:**
- `psycopg3` — асинхронный адаптер для PostgreSQL
- `psycopg_pool.AsyncConnectionPool` — пул соединений
- `dict_row` — результаты запросов в виде словарей

### Основные функции

#### Инициализация и закрытие

```python
async def init_db() -> None:
    """Инициализирует пул соединений с БД"""

async def close_db() -> None:
    """Закрывает пул соединений"""
```

#### Работа с пользователями

```python
async def get_or_create_user(telegram_user_id: int, first_name: str) -> int:
    """Получает ID пользователя или создает нового"""

async def get_user_by_telegram_id(telegram_user_id: int) -> dict[str, Any] | None:
    """Получает пользователя по Telegram ID"""
```

#### Работа с чатами

```python
async def get_or_create_chat(telegram_chat_id: int) -> int:
    """Получает ID чата или создает новый"""

async def get_chat_by_telegram_id(telegram_chat_id: int) -> dict[str, Any] | None:
    """Получает чат по Telegram ID"""
```

#### Работа с сообщениями

```python
async def save_message(user_id: int, chat_id: int, role: str, content: str) -> int:
    """Сохраняет сообщение в БД"""

async def get_messages(user_id: int, chat_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """Получает последние сообщения диалога"""

async def soft_delete_messages(user_id: int, chat_id: int) -> None:
    """Выполняет мягкое удаление сообщений"""
```

### Пример использования

```python
from services.database import close_db, get_or_create_user, init_db, save_message

# При запуске бота
await init_db()

# Работа с данными
user_id = await get_or_create_user(123456, "Ivan")
chat_id = await get_or_create_chat(789012)
message_id = await save_message(user_id, chat_id, "user", "Привет!")

# При остановке бота
await close_db()
```

---

## Интеграция с сервисом контекста

Файл: `services/context.py`

Сервис контекста (`services/context.py`) теперь использует DAL вместо in-memory хранилища.

### Основные изменения

**До (in-memory):**
```python
user_contexts: dict[tuple[int, int], dict] = {}

def get_context(user_id: int, chat_id: int) -> dict:
    return user_contexts.get((user_id, chat_id), {"messages": []})
```

**После (PostgreSQL):**
```python
async def get_context(user_id: int, chat_id: int) -> dict:
    db_user_id = await get_or_create_user(user_id, "Unknown")
    db_chat_id = await get_or_create_chat(chat_id)
    db_messages = await get_messages(db_user_id, db_chat_id, limit=100)
    # Преобразование в формат OpenAI
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in db_messages]
    return {"messages": messages}
```

### Инкрементальное сохранение

Сервис контекста сохраняет **только новые** сообщения, избегая дублирования:

```python
async def save_context(user_id: int, chat_id: int, messages: list[Message], user_name: str | None = None) -> None:
    # Получить существующие сообщения
    existing_messages = await get_messages(db_user_id, db_chat_id, limit=100)
    existing_count = len(existing_messages)

    # Сохранить только новые
    new_messages = messages[existing_count:]
    for msg in new_messages:
        await save_message(db_user_id, db_chat_id, msg["role"], msg["content"])
```

---

## Тестирование

Файл: `tests/test_database.py`

### Подход к тестированию

Тесты используют **моки** для имитации базы данных, избегая зависимости от реального PostgreSQL:

```python
@pytest.fixture(autouse=True)
async def mock_db_pool():
    """Фикстура для мокирования пула соединений БД."""
    with patch("psycopg_pool.AsyncConnectionPool", autospec=True) as MockPool:
        mock_pool_instance = MockPool.return_value
        # ... настройка моков ...
        yield mock_pool_instance
```

### Примеры тестов

```python
@pytest.mark.asyncio
async def test_save_message(mock_db_pool):
    """Тест сохранения сообщения."""
    mock_db_pool.connection.return_value.__aenter__.return_value.cursor.return_value.__aenter__.return_value.fetchone.return_value = {"id": 1}
    message_id = await save_message(1, 1, "user", "Hello")
    assert message_id == 1
    # Проверяем, что длина сообщения сохранена
    args, kwargs = mock_db_pool.connection.return_value.__aenter__.return_value.cursor.return_value.__aenter__.return_value.execute.call_args
    assert args[1][4] == len("Hello")
```

### Запуск тестов

```bash
# Все тесты
uv run pytest tests/ -v

# Только тесты БД
uv run pytest tests/test_database.py -v

# С покрытием
uv run pytest tests/ --cov=services.database --cov-report=html
```

---

## Soft Delete

### Принцип работы

Вместо физического удаления записей из БД, мы устанавливаем значение поля `deleted_at`:

```sql
-- "Удаление" сообщения
UPDATE messages
SET deleted_at = NOW()
WHERE user_id = ? AND chat_id = ? AND deleted_at IS NULL;
```

### Получение активных записей

Все запросы фильтруют удалённые записи:

```sql
SELECT * FROM messages
WHERE user_id = ? AND chat_id = ? AND deleted_at IS NULL
ORDER BY created_at DESC;
```

### Преимущества

- ✅ **Восстановление данных** — можно отменить удаление
- ✅ **Аудит** — история операций сохраняется
- ✅ **Безопасность** — случайное удаление не приводит к потере данных
- ✅ **Аналитика** — можно анализировать удалённые данные

### Физическая очистка (опционально)

Для физического удаления старых "мягко удалённых" записей (например, старше 30 дней):

```sql
DELETE FROM messages
WHERE deleted_at IS NOT NULL
AND deleted_at < NOW() - INTERVAL '30 days';
```

⚠️ **Внимание:** Эта операция необратима! Выполняйте только если уверены.

---

## Troubleshooting

### PostgreSQL не запускается

1. Проверьте, что Docker запущен:
   ```bash
   docker ps
   ```

2. Проверьте логи:
   ```bash
   docker-compose logs db
   ```

3. Убедитесь, что порт 5432 свободен:
   ```bash
   netstat -an | find "5432"
   ```

### Ошибки миграций

1. Проверьте текущую версию БД:
   ```bash
   uv run alembic current
   ```

2. Проверьте историю миграций:
   ```bash
   uv run alembic history
   ```

3. Если миграция застряла, откатите и примените заново:
   ```bash
   uv run alembic downgrade -1
   uv run alembic upgrade head
   ```

### Проблемы с подключением

1. Проверьте `DATABASE_URL` в `.env`:
   ```ini
   DATABASE_URL=postgresql://user:password@localhost:5432/systtechbot_db
   ```

2. Проверьте подключение напрямую через psql:
   ```bash
   psql postgresql://user:password@localhost:5432/systtechbot_db
   ```

3. Убедитесь, что БД готова (подождите 5-10 секунд после `docker-compose up`).

### Очистка и пересоздание БД

Если ничего не помогает, выполните полный сброс:

```bash
make db-reset
```

Или вручную:
```bash
docker-compose down -v  # Удаляет БД и volumes!
docker-compose up -d
# Подождите 5-10 секунд
uv run alembic upgrade head
```

---

## Best Practices

### 1. Всегда используйте пул соединений

✅ **Правильно:**
```python
pool = await get_pool()
async with pool.connection() as conn:
    # Работа с БД
```

❌ **Неправильно:**
```python
conn = await psycopg.AsyncConnection.connect(DATABASE_URL)
# Отдельное соединение для каждого запроса (медленно!)
```

### 2. Используйте транзакции для связанных операций

```python
async with pool.connection() as conn:
    async with conn.transaction():
        user_id = await get_or_create_user(conn, ...)
        chat_id = await get_or_create_chat(conn, ...)
        await save_message(conn, user_id, chat_id, ...)
```

### 3. Не забывайте про индексы

При добавлении новых запросов, проверьте, нужны ли новые индексы:

```sql
-- Пример: часто фильтруете по role?
CREATE INDEX idx_messages_role ON messages(role, deleted_at);
```

### 4. Используйте параметризованные запросы

✅ **Правильно:**
```python
await cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

❌ **Неправильно (SQL injection!):**
```python
await cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 5. Логируйте SQL ошибки

```python
try:
    await cur.execute(query, params)
except psycopg.Error as e:
    logger.error(f"Database error: {e}")
    raise
```

---

## Дальнейшее развитие

### Потенциальные улучшения

1. **Индексы для полнотекстового поиска**
   ```sql
   CREATE INDEX idx_messages_content_gin ON messages USING GIN(to_tsvector('russian', content));
   ```

2. **Партиционирование таблицы messages**
   - По дате (`created_at`)
   - Для больших объёмов данных

3. **Репликация и отказоустойчивость**
   - Master-Slave репликация
   - Backup & Restore стратегия

4. **Кэширование**
   - Redis для кэширования часто запрашиваемых данных
   - Снижение нагрузки на БД

5. **Мониторинг производительности**
   - `pg_stat_statements` для анализа медленных запросов
   - Grafana + Prometheus для метрик

---

## Полезные ссылки

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg3 Documentation](https://www.psycopg.org/psycopg3/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [ADR-03: Стратегия хранения контекста](../adrs/ADR-03.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Версия:** 1.0 (Sprint S1)
**Дата:** 2025-10-16
