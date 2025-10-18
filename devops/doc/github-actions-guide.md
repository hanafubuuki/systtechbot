# GitHub Actions: Руководство для проекта systtechbot

## Введение в GitHub Actions

**GitHub Actions** — это встроенная CI/CD платформа GitHub, позволяющая автоматизировать сборку, тестирование и развертывание кода прямо из репозитория.

### Ключевые концепции

- **Workflow (Рабочий процесс)** — автоматизированный процесс, состоящий из одной или нескольких задач
- **Job (Задача)** — набор шагов, выполняющихся на одном runner
- **Step (Шаг)** — отдельная команда или action
- **Action** — переиспользуемый модуль для выполнения типовых задач
- **Runner** — виртуальная машина (Ubuntu, Windows, macOS), где выполняется workflow

### Структура Workflow

Workflow определяются в YAML файлах в директории `.github/workflows/`:

```yaml
name: Build and Publish
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: docker build .
```

## Triggers (Триггеры)

Workflow может запускаться автоматически при различных событиях:

### Push события

```yaml
on:
  push:
    branches:
      - main
      - develop
```

Запуск при push в указанные ветки.

### Pull Request события

```yaml
on:
  pull_request:
    branches:
      - main
```

Запуск при создании или обновлении Pull Request в ветку main. Позволяет проверить изменения перед слиянием.

### Ручной запуск (workflow_dispatch)

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

Позволяет запускать workflow вручную через GitHub UI с параметрами.

### Комбинирование триггеров

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

Workflow запустится при push в main, при PR в main, или вручную.

## GitHub Container Registry (ghcr.io)

**GitHub Container Registry** — встроенный Docker registry для хранения container образов.

### Преимущества ghcr.io

- ✅ Бесплатный для публичных репозиториев
- ✅ Интегрирован с GitHub (не нужны отдельные аккаунты)
- ✅ Автоматическая аутентификация через GITHUB_TOKEN
- ✅ Поддержка публичных и приватных образов
- ✅ Неограниченное хранение публичных образов

### Адреса образов

Формат: `ghcr.io/OWNER/IMAGE_NAME:TAG`

Примеры:
- `ghcr.io/hanafubuuki/systtechbot-bot:latest`
- `ghcr.io/hanafubuuki/systtechbot-api:v1.2.3`
- `ghcr.io/hanafubuuki/systtechbot-frontend:sha-abc123`

### Public vs Private образы

**Private (по умолчанию):**
- Доступны только пользователям с правами на репозиторий
- Требуют аутентификации для `docker pull`

**Public:**
- Доступны всем без аутентификации
- Можно скачать командой `docker pull` без логина
- Настраивается через Package settings в GitHub UI

### Настройка прав доступа для GITHUB_TOKEN

GitHub автоматически создает токен `GITHUB_TOKEN` для каждого workflow run.

**По умолчанию** токен имеет права на:
- Чтение кода репозитория
- Запись в GitHub Container Registry

**Для публикации образов** нужно:

1. В настройках репозитория: `Settings` → `Actions` → `General`
2. Секция "Workflow permissions"
3. Выбрать: **"Read and write permissions"**
4. Сохранить изменения

Альтернативно, можно явно указать permissions в workflow:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      # ...
```

## Matrix Strategy (Матричная стратегия)

Matrix strategy позволяет запускать одну и ту же job с разными параметрами параллельно.

### Пример: сборка нескольких образов

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, api, frontend]
    steps:
      - name: Build ${{ matrix.service }}
        run: |
          docker build -f devops/dockerfiles/${{ matrix.service }}.Dockerfile .
```

Создаст 3 параллельных job: один для bot, один для api, один для frontend.

### Преимущества matrix

- ⚡ Параллельное выполнение (быстрее)
- 📦 Меньше дублирования кода
- 🔄 Легко добавить новый сервис

### Настройка matrix

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    # Опционально: не прерывать все job при ошибке в одном
    fail-fast: false
```

## Docker Layer Caching

Docker layer caching ускоряет повторные сборки, переиспользуя ранее собранные слои.

### Настройка через Docker Buildx

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: ghcr.io/user/image:latest
    cache-from: type=registry,ref=ghcr.io/user/image:buildcache
    cache-to: type=registry,ref=ghcr.io/user/image:buildcache,mode=max
```

### Как это работает

1. **cache-from**: При сборке Docker проверяет registry на наличие закэшированных слоев
2. **cache-to**: После сборки Docker сохраняет слои обратно в registry
3. При следующей сборке переиспользуются неизменившиеся слои

### Эффект

- 🚀 Первая сборка: 5-10 минут
- ⚡ Повторная сборка (без изменений): 30 секунд
- 🔄 Сборка с небольшими изменениями: 1-3 минуты

## Тегирование образов

### Стратегии тегирования

**Latest (последняя версия):**
```yaml
tags: ghcr.io/user/image:latest
```
Обновляется при каждой сборке из main ветки.

**Commit SHA:**
```yaml
tags: ghcr.io/user/image:sha-${{ github.sha }}
```
Уникальный тег для каждого коммита. Позволяет откатиться на любую версию.

**Pull Request:**
```yaml
tags: ghcr.io/user/image:pr-${{ github.event.pull_request.number }}
```
Временный тег для тестирования PR перед слиянием.

**Версии (semver):**
```yaml
tags: ghcr.io/user/image:v1.2.3
```
При релизах с git tags.

### Множественные теги

Можно публиковать один образ с несколькими тегами:

```yaml
tags: |
  ghcr.io/user/image:latest
  ghcr.io/user/image:sha-${{ github.sha }}
  ghcr.io/user/image:${{ github.ref_name }}
```

## Пример полного Workflow

```yaml
name: Build and Publish Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    strategy:
      matrix:
        service: [bot, api, frontend]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate Docker tags
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/systtechbot-${{ matrix.service }}
          tags: |
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
            type=sha,prefix=sha-
            type=ref,event=pr,prefix=pr-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: devops/dockerfiles/${{ matrix.service }}.Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=ghcr.io/${{ github.repository_owner }}/systtechbot-${{ matrix.service }}:buildcache
          cache-to: type=registry,ref=ghcr.io/${{ github.repository_owner }}/systtechbot-${{ matrix.service }}:buildcache,mode=max
```

## Полезные GitHub Actions

### Официальные actions

- `actions/checkout@v4` — клонирование репозитория
- `actions/setup-node@v4` — установка Node.js
- `actions/setup-python@v5` — установка Python
- `actions/cache@v4` — кэширование зависимостей

### Docker actions

- `docker/setup-buildx-action@v3` — настройка Docker Buildx
- `docker/login-action@v3` — вход в Docker registry
- `docker/build-push-action@v5` — сборка и публикация образа
- `docker/metadata-action@v5` — генерация тегов и labels

## Отладка Workflow

### Просмотр логов

1. Перейти в `Actions` tab репозитория
2. Выбрать workflow run
3. Кликнуть на job для просмотра логов

### Локальная отладка

Использовать [act](https://github.com/nektos/act) для запуска workflow локально:

```bash
# Установка act
brew install act  # macOS
# или
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Запуск workflow
act -W .github/workflows/build.yml
```

### Debug логирование

Включить подробное логирование через секрет:
```
ACTIONS_STEP_DEBUG = true
ACTIONS_RUNNER_DEBUG = true
```

## Лучшие практики

1. ✅ **Используйте конкретные версии actions** (`@v4` вместо `@latest`)
2. ✅ **Кэширование** — ускоряет повторные сборки
3. ✅ **Matrix** — для параллельных задач
4. ✅ **Минимальные permissions** — указывайте только необходимые права
5. ✅ **Secrets** — никогда не коммитьте токены, используйте GitHub Secrets
6. ✅ **Fail-fast: false** — для matrix, если хотите видеть все ошибки
7. ✅ **Timeout** — установите разумный timeout (default: 6 часов)

## Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry Guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Awesome GitHub Actions](https://github.com/sdras/awesome-actions)

---

**Дата создания:** 2025-10-18
**Спринт:** D1 - Build & Publish

