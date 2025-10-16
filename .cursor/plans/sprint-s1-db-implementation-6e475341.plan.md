<!-- 6e475341-a552-4293-a884-fd56eb6b3e96 fb0972e4-1226-4f75-b7bf-e16b5819d6ee -->
# Sprint S1: Персистентное хранение данных

## Цель

Заменить in-memory хранение контекста диалогов на PostgreSQL с сохранением между перезапусками бота.

## Технологический стек

- **БД:** PostgreSQL 16
- **Миграции:** Alembic
- **Доступ к данным:** Raw SQL (без ORM)
- **Подход:** Soft delete, tracking created_at и length

## Итерации

### Итерация 1: Инфраструктура и документация

**1.1. Создать ADR-03: Выбор PostgreSQL + Alembic**

- Файл: `doc/adrs/ADR-03.md`
- Обоснование выбора PostgreSQL vs SQLite
- Обоснование выбора Alembic vs custom migrations
- Обоснование raw SQL vs ORM

**1.2. Настроить Docker Compose**

- Файл: `docker-compose.yml`
- PostgreSQL 16 с persistent volume
- Переменные окружения (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)
- Порт 5432

**1.3. Добавить зависимости**

- Обновить `pyproject.toml`:
  - `psycopg[binary]>=3.1.0` (PostgreSQL драйвер)
  - `alembic>=1.13.0` (миграции)

### Итерация 2: Проектирование схемы БД

**2.1. Спроектировать схему**

Три таблицы (KISS подход):

```sql
-- users: пользователи Telegram
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL UNIQUE,
    first_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- chats: чаты Telegram
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    telegram_chat_id BIGINT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- messages: сообщения диалогов
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    chat_id INTEGER NOT NULL REFERENCES chats(id),
    role VARCHAR(20) NOT NULL,  -- system/user/assistant
    content TEXT NOT NULL,
    length INTEGER NOT NULL,     -- длина в символах
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,        -- soft delete
    INDEX idx_user_chat (user_id, chat_id, deleted_at, created_at)
);
```

**2.2. Обновить .env.example**

- Добавить `DATABASE_URL=postgresql://user:password@localhost:5432/systtechbot`
- Добавить комментарии для новых переменных

### Итерация 3: Настройка Alembic

**3.1. Инициализировать Alembic**

```bash
alembic init alembic
```

**3.2. Настроить alembic.ini**

- Убрать hardcoded sqlalchemy.url
- Использовать sqlalchemy.url из env.py

**3.3. Настроить alembic/env.py**

- Загружать DATABASE_URL из config.py
- Настроить target_metadata (оставить None для raw SQL)

**3.4. Создать первую миграцию**

```bash
alembic revision -m "create_initial_schema"
```

- Файл: `alembic/versions/001_create_initial_schema.py`
- upgrade(): CREATE TABLE для users, chats, messages
- downgrade(): DROP TABLE

### Итерация 4: Data Access Layer

**4.1. Создать services/database.py**

Модуль с raw SQL функциями:

```python
# Connection management
async def get_connection() -> AsyncConnection
async def init_db() -> None

# Users
async def get_or_create_user(telegram_user_id: int, first_name: str) -> int
async def get_user_by_telegram_id(telegram_user_id: int) -> dict | None

# Chats
async def get_or_create_chat(telegram_chat_id: int) -> int
async def get_chat_by_telegram_id(telegram_chat_id: int) -> dict | None

# Messages
async def save_message(user_id: int, chat_id: int, role: str, content: str) -> int
async def get_messages(user_id: int, chat_id: int, limit: int = 10) -> list[dict]
async def soft_delete_messages(user_id: int, chat_id: int) -> None
```

**Технические детали:**

- Использовать `psycopg` с async support
- Connection pool через singleton pattern
- Все запросы через prepared statements (защита от SQL injection)
- Автоматически вычислять length = len(content)

**4.2. Обновить config.py**

- Добавить `database_url: str` в класс Config
- Валидация DATABASE_URL при загрузке

### Итерация 5: Рефакторинг context.py

**5.1. Обновить services/context.py**

Заменить in-memory storage на БД:

```python
# Убрать глобальный словарь user_contexts
# Переписать функции:

async def get_context(user_id: int, chat_id: int) -> dict:
    # Вызвать database.get_messages()
    # Вернуть {"messages": [...]}

async def save_context(user_id: int, chat_id: int, messages: list[Message], user_name: str | None = None) -> None:
    # Сохранить пользователя через database.get_or_create_user()
    # Сохранить чат через database.get_or_create_chat()
    # Сохранить новые сообщения через database.save_message()

async def clear_context(user_id: int, chat_id: int) -> None:
    # Вызвать database.soft_delete_messages()
```

**5.2. Обновить handlers/messages.py**

- Изменить вызовы на async: `await get_context()`, `await save_context()`, `await clear_context()`

**5.3. Обновить handlers/commands.py**

- Изменить вызов clear_context на async: `await clear_context()`

**5.4. Обновить bot.py**

- Добавить инициализацию БД: `await init_db()` перед запуском polling

### Итерация 6: Тестирование

**6.1. Обновить тесты**

- `tests/test_context.py`: использовать test database или mocker
- `tests/test_database.py`: новые тесты для database.py
- Использовать pytest-asyncio для async тестов
- Создать фикстуры для test DB

**6.2. Добавить integration тесты**

- Тест полного флоу: отправка сообщения → сохранение в БД → получение из БД
- Тест soft delete
- Тест created_at и length

### Итерация 7: Документация

**7.1. Создать migration guide**

- Файл: `doc/guides/06-DATABASE.md`
- Как запустить PostgreSQL через Docker
- Как применить миграции
- Как откатить миграции
- Структура БД и индексы

**7.2. Обновить README.md**

- Добавить секцию "База данных"
- Обновить "Быстрый старт" с запуском Docker
- Добавить команды Makefile для БД

**7.3. Обновить doc/guides/02-ARCHITECTURE.md**

- Заменить "In-memory хранение" на "PostgreSQL"
- Добавить database.py в схему модулей
- Обновить диаграммы

**7.4. Актуализировать doc/vision.md**

- Раздел "Хранение данных": заменить "In-Memory" на "PostgreSQL"
- Раздел "Архитектура": добавить слой Data Access (database.py)
- Раздел "Структура проекта": добавить services/database.py
- Обновить секцию "Зависимости": добавить psycopg и alembic

**7.5. Актуализировать doc/idea.md**

- Раздел "Стек технологий": добавить PostgreSQL + Alembic (если нужно)
- Убедиться, что описание соответствует реальной архитектуре

**7.6. Добавить ссылку на план в doc/roadmap.md**

- В таблице спринтов для S1 в колонке "Фактический план"
- Добавить ссылку на `.cursor/plans/sprint-s1-db-implementation-6e475341.plan.md`

**7.7. Создать doc/tasklists/tasklist-S1.md**

- Детальный список всех выполненных задач спринта

### Итерация 8: Makefile и финальная полировка

**8.1. Обновить Makefile**

```makefile
db-up:      # Запустить PostgreSQL
db-down:    # Остановить PostgreSQL
db-migrate: # Применить миграции
db-reset:   # Сбросить БД и применить миграции заново
```

**8.2. Финальная проверка .env.example**

- Убедиться, что все переменные окружения задокументированы
- Проверить корректность значений по умолчанию
- Добавить полезные комментарии для пользователей

**8.3. Запустить quality checks**

```bash
make format
make lint
make typecheck
```

**8.4. Обновить .gitignore**

- Добавить `alembic/versions/*.pyc`
- Добавить `postgres-data/` (если volume локальный)

**8.5. Запустить полные тесты**

```bash
make test
make coverage  # Убедиться  что coverage >= 80%
```

**8.6. Финальная проверка**

- Проверить все критерии приёмки
- Убедиться, что бот работает после перезапуска
- Проверить, что команда /clear делает soft delete
- Запустить Docker Compose и применить миграции

## Критерии приёмки

**Функциональность:**

- [ ] PostgreSQL запускается через Docker Compose
- [ ] Alembic настроен, миграции работают
- [ ] История диалогов сохраняется в БД
- [ ] Бот работает после перезапуска (контекст восстанавливается)
- [ ] Команда /clear делает soft delete (deleted_at заполняется)
- [ ] У каждого сообщения есть created_at и length

**Качество кода:**

- [ ] Все тесты проходят (coverage >= 80%)
- [ ] Quality checks проходят (ruff, mypy)

**Документация:**

- [ ] Создан ADR-03 с обоснованием технологических выборов
- [ ] Создан doc/guides/06-DATABASE.md с инструкциями по работе с БД
- [ ] Обновлен README.md с информацией о запуске PostgreSQL
- [ ] Обновлен doc/guides/02-ARCHITECTURE.md (PostgreSQL вместо in-memory)
- [ ] Актуализирован doc/vision.md (отражает использование PostgreSQL)
- [ ] Актуализирован doc/idea.md (при необходимости)
- [ ] Добавлена ссылка на план спринта в doc/roadmap.md
- [ ] Создан doc/tasklists/tasklist-S1.md с детальным списком задач

## Ключевые файлы

**Новые:**

- `docker-compose.yml`
- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/001_*.py`
- `services/database.py`
- `tests/test_database.py`
- `doc/adrs/ADR-03.md`
- `doc/guides/06-DATABASE.md`
- `doc/tasklists/tasklist-S1.md`

**Изменяемые:**

- `pyproject.toml` (зависимости)
- `config.py` (DATABASE_URL)
- `services/context.py` (БД вместо in-memory)
- `handlers/messages.py` (async calls)
- `handlers/commands.py` (async calls)
- `bot.py` (init_db)
- `tests/test_context.py` (обновить тесты)
- `README.md` (секция "База данных")
- `doc/guides/02-ARCHITECTURE.md` (PostgreSQL вместо in-memory)
- `doc/vision.md` (актуализация хранения данных)
- `doc/idea.md` (актуализация при необходимости)
- `doc/roadmap.md` (ссылка на план спринта)
- `Makefile` (команды для БД)
- `.env.example` (DATABASE_URL)
- `.gitignore` (alembic, postgres-data)

### To-dos

- [ ] 1.1. Создать ADR-03 с обоснованием PostgreSQL vs SQLite, Alembic vs custom, raw SQL vs ORM
- [ ] 1.2. Создать docker-compose.yml с PostgreSQL 16, persistent volume, переменными окружения
- [ ] 1.3. Добавить psycopg[binary]>=3.1.0 и alembic>=1.13.0 в pyproject.toml
- [ ] 2.1. Спроектировать схему БД: users, chats, messages (с soft delete, created_at, length)
- [ ] 2.2. Обновить .env.example: добавить DATABASE_URL с комментариями
- [ ] 3.1. Инициализировать Alembic (alembic init alembic)
- [ ] 3.2. Настроить alembic.ini (убрать hardcoded sqlalchemy.url)
- [ ] 3.3. Настроить alembic/env.py (загрузка DATABASE_URL из config.py)
- [ ] 3.4. Создать первую миграцию 001_create_initial_schema.py (upgrade/downgrade)
- [ ] 4.1. Создать services/database.py с функциями: connection management, users, chats, messages
- [ ] 4.2. Добавить database_url в config.py с валидацией
- [ ] 5.1. Рефакторить services/context.py: убрать user_contexts, использовать database.py
- [ ] 5.2. Обновить handlers/messages.py: async calls к get_context/save_context
- [ ] 5.3. Обновить handlers/commands.py: async call к clear_context
- [ ] 5.4. Обновить bot.py: добавить await init_db() перед polling
- [ ] 6.1. Обновить tests/test_context.py для работы с БД (test database или mocker)
- [ ] 6.2. Создать tests/test_database.py с тестами для database.py, pytest-asyncio, фикстуры
- [ ] 7.1. Создать doc/guides/06-DATABASE.md с инструкциями по работе с БД
- [ ] 7.2. Обновить README.md (добавить секцию "База данных", команды Makefile)
- [ ] 7.3. Обновить doc/guides/02-ARCHITECTURE.md (PostgreSQL, database.py, диаграммы)
- [ ] 7.4. Актуализировать doc/vision.md (хранение данных, архитектура, зависимости)
- [ ] 7.5. Актуализировать doc/idea.md (стек технологий, проверка соответствия)
- [ ] 7.6. Добавить ссылку на план в doc/roadmap.md (колонка "Фактический план" для S1)
- [ ] 7.7. Создать doc/tasklists/tasklist-S1.md с детальным списком задач
- [ ] 8.1. Обновить Makefile: добавить команды db-up, db-down, db-migrate, db-reset
- [ ] 8.2. Финальная проверка .env.example (все переменные задокументированы, комментарии)
- [ ] 8.3. Запустить quality checks: make format, make lint, make typecheck
- [ ] 8.4. Обновить .gitignore: alembic/versions/*.pyc, postgres-data/
- [ ] 8.5. Запустить полные тесты: make test (coverage >= 80%)
- [ ] 8.6. Проверить все критерии приёмки