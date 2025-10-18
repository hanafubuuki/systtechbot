# Docker Setup для systtechbot

Эта директория содержит Docker инфраструктуру для запуска всех сервисов systtechbot локально.

## 🚀 Быстрый старт

У systtechbot есть два режима работы:

1. **Local mode** - локальная сборка образов из исходного кода (для разработки)
2. **Production mode** - использование готовых образов из GitHub Container Registry (для запуска)

### Вариант 1: Production mode (рекомендуется для быстрого старта) 🚀

Самый быстрый способ - использовать готовые образы из GitHub Container Registry:

#### 1. Подготовка окружения

```bash
cd devops
cp env.example .env
# Отредактируйте .env и заполните TELEGRAM_TOKEN и OPENAI_API_KEY
```

#### 2. Скачивание и запуск образов

```bash
# Переключиться в production режим
./scripts/switch-mode.sh prod

# Скачать последние образы
docker-compose -f docker-compose.current.yml pull

# Запустить все сервисы
docker-compose -f docker-compose.current.yml up
```

Или в фоновом режиме:
```bash
docker-compose -f docker-compose.current.yml up -d
```

#### 3. Запуск конкретной версии

Вы можете запустить любую версию по тегу:

```bash
# Последняя стабильная версия из main
IMAGE_TAG=latest docker-compose -f docker-compose.prod.yml up

# Конкретный коммит
IMAGE_TAG=sha-abc1234 docker-compose -f docker-compose.prod.yml up

# Версия из Pull Request
IMAGE_TAG=pr-45 docker-compose -f docker-compose.prod.yml up
```

### Вариант 2: Local mode (для разработки) 🛠️

Если вы разрабатываете проект и хотите собирать образы из исходников:

#### 1. Подготовка окружения

```bash
cd devops
cp env.example .env
# Отредактируйте .env и заполните TELEGRAM_TOKEN и OPENAI_API_KEY
```

#### 2. Локальная сборка и запуск

```bash
# Переключиться в local режим
./scripts/switch-mode.sh local

# Собрать и запустить
docker-compose -f docker-compose.current.yml up --build
```

Или просто:
```bash
docker-compose up --build
```

### 4. Проверка работоспособности

После запуска все сервисы будут доступны:

- **Frontend**: http://localhost:3000 - веб-интерфейс дашборда
- **API**: http://localhost:8000 - REST API для статистики
- **API Docs**: http://localhost:8000/docs - интерактивная документация Swagger
- **PostgreSQL**: localhost:5432 - база данных
- **Bot**: работает в фоне, проверяйте логи

## 📊 Сервисы

### 1. PostgreSQL (postgres)
- База данных для хранения диалогов и статистики
- Порт: 5432
- Автоматический healthcheck
- Persistent volume для сохранения данных

### 2. Telegram Bot (bot)
- Python бот для обработки сообщений в Telegram
- Автоматически подключается к БД после её готовности
- Выполняет миграции при первом запуске

### 3. FastAPI (api)
- REST API для получения статистики
- Порт: 8000
- Интерактивная документация: /docs
- Поддержка CORS для фронтенда

### 4. Next.js Frontend (frontend)
- Современный веб-интерфейс дашборда
- Порт: 3000
- Автоматически подключается к API

## 🔧 Полезные команды

### Переключение между режимами

```bash
# Показать текущий режим
./scripts/switch-mode.sh

# Переключиться на production (registry образы)
./scripts/switch-mode.sh prod

# Переключиться на local (локальная сборка)
./scripts/switch-mode.sh local
```

### Работа с образами из GitHub Container Registry

#### Скачивание образов

```bash
# Скачать все образы
docker-compose -f docker-compose.prod.yml pull

# Скачать конкретный сервис
docker-compose -f docker-compose.prod.yml pull bot
docker-compose -f docker-compose.prod.yml pull api
docker-compose -f docker-compose.prod.yml pull frontend
```

#### Ручное скачивание образов

Образы доступны публично и не требуют авторизации:

```bash
# Скачать последнюю версию
docker pull ghcr.io/hanafubuuki/systtechbot-bot:latest
docker pull ghcr.io/hanafubuuki/systtechbot-api:latest
docker pull ghcr.io/hanafubuuki/systtechbot-frontend:latest

# Скачать конкретную версию по SHA
docker pull ghcr.io/hanafubuuki/systtechbot-bot:sha-abc1234

# Скачать версию из Pull Request
docker pull ghcr.io/hanafubuuki/systtechbot-bot:pr-45
```

#### Просмотр доступных тегов

Посетите GitHub Container Registry:
- https://github.com/hanafubuuki/systtechbot/pkgs/container/systtechbot-bot
- https://github.com/hanafubuuki/systtechbot/pkgs/container/systtechbot-api
- https://github.com/hanafubuuki/systtechbot/pkgs/container/systtechbot-frontend

### Просмотр логов

Все сервисы:
```bash
docker-compose logs -f
```

Конкретный сервис:
```bash
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Остановка сервисов

```bash
docker-compose down
```

Остановка с удалением volumes (⚠️ удалит все данные БД):
```bash
docker-compose down -v
```

### Пересборка образов

После изменения кода:
```bash
docker-compose up --build
```

Пересборка конкретного сервиса:
```bash
docker-compose build bot
docker-compose up bot
```

### Перезапуск сервиса

```bash
docker-compose restart bot
docker-compose restart api
docker-compose restart frontend
```

### Выполнение команд внутри контейнера

Войти в контейнер:
```bash
docker-compose exec bot bash
docker-compose exec api bash
docker-compose exec postgres psql -U systtechbot -d systtechbot
```

Запустить команду:
```bash
docker-compose exec bot python -c "import sys; print(sys.version)"
docker-compose exec api uv run alembic current
```

## 🐛 Устранение проблем

### Проблема: PostgreSQL не запускается

**Симптомы**: Ошибки подключения к БД в логах bot/api

**Решение**:
1. Проверьте, что порт 5432 не занят:
   ```bash
   # Windows
   netstat -ano | findstr :5432

   # Linux/Mac
   lsof -i :5432
   ```
2. Если порт занят, остановите локальный PostgreSQL или измените порт в docker-compose.yml
3. Проверьте логи postgres:
   ```bash
   docker-compose logs postgres
   ```

### Проблема: Ошибки миграций БД

**Симптомы**: Bot/API не могут подключиться к БД, ошибки таблиц

**Решение**:
1. Убедитесь, что PostgreSQL здоров:
   ```bash
   docker-compose ps
   ```
2. Выполните миграции вручную:
   ```bash
   docker-compose exec bot uv run alembic upgrade head
   ```
   или
   ```bash
   docker-compose exec api uv run alembic upgrade head
   ```

### Проблема: Frontend не подключается к API

**Симптомы**: Ошибки CORS, не загружаются данные

**Решение**:
1. Проверьте, что API запущен:
   ```bash
   curl http://localhost:8000/health
   ```
2. Проверьте переменную окружения в .env:
   ```env
   API_CORS_ORIGINS=http://localhost:3000
   ```
3. Перезапустите API:
   ```bash
   docker-compose restart api
   ```

### Проблема: Порты уже заняты

**Симптомы**: Ошибка при запуске "port is already allocated"

**Решение**:
1. Проверьте занятые порты:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   netstat -ano | findstr :5432

   # Linux/Mac
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```
2. Остановите процессы на этих портах или измените порты в docker-compose.yml:
   ```yaml
   ports:
     - "3001:3000"  # Изменить внешний порт
   ```

### Проблема: Недостаточно места на диске

**Симптомы**: Ошибки при сборке образов

**Решение**:
1. Очистите неиспользуемые образы:
   ```bash
   docker system prune -a
   ```
2. Удалите старые volumes:
   ```bash
   docker volume prune
   ```

### Проблема: Медленная сборка

**Решение**:
1. Используйте кэш Docker правильно - не изменяйте pyproject.toml/package.json без необходимости
2. Первая сборка всегда долгая, последующие будут быстрее благодаря кэшу

## 📁 Структура директории

```
devops/
├── docker-compose.yml        # Локальная сборка (local mode)
├── docker-compose.prod.yml   # Production с registry образами
├── docker-compose.current.yml # Симлинк на активный режим
├── env.example               # Пример переменных окружения
├── .env                      # Ваши переменные (не в git)
├── .dockerignore            # Исключения для Docker сборки
├── dockerfiles/
│   ├── bot.Dockerfile        # Dockerfile для Telegram бота
│   ├── api.Dockerfile        # Dockerfile для API
│   └── frontend.Dockerfile   # Dockerfile для Frontend
├── scripts/
│   ├── switch-mode.sh        # Переключение между local/prod
│   └── wait-for-db.sh        # Скрипт ожидания БД
├── doc/
│   ├── github-actions-guide.md  # Руководство по CI/CD
│   ├── devops-roadmap.md        # DevOps roadmap
│   └── plans/                   # Планы спринтов
└── README.md                 # Эта документация
```

## 🔐 Безопасность

⚠️ **Важно для продакшн**:

1. Измените пароли в `.env` на безопасные
2. Не коммитьте `.env` в git
3. Используйте secrets management для продакшн
4. Настройте SSL/TLS для внешних подключений

## 📚 Дополнительная информация

- **CI/CD:** Автоматическая сборка образов через GitHub Actions - см. [GitHub Actions Guide](doc/github-actions-guide.md)
- **Registry:** Образы публикуются в GitHub Container Registry (ghcr.io) - публичный доступ
- **Roadmap:** См. [DevOps Roadmap](doc/devops-roadmap.md) для планов будущих спринтов
- **Продакшн:** Для ручного развертывания см. Sprint D2
- **Auto Deploy:** Для автоматического развертывания см. Sprint D3

## 🆘 Поддержка

Если проблема не решается:

1. Проверьте логи всех сервисов: `docker-compose logs`
2. Убедитесь, что `.env` файл заполнен корректно
3. Попробуйте пересоздать контейнеры: `docker-compose down && docker-compose up --build`
4. Проверьте документацию проекта в `/doc`

