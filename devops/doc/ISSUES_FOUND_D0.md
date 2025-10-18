# Проблемы найденные при тестировании Docker Setup

## Дата: 2025-10-18

## Найденные проблемы

### 1. PATH для UV был неправильным ❌ → ✅ ИСПРАВЛЕНО

**Проблема:**
```dockerfile
ENV PATH="/root/.cargo/bin:$PATH"  # ❌ Неправильно!
```

UV устанавливается в `/root/.local/bin`, а не в `/root/.cargo/bin`.

**Решение:**
```dockerfile
ENV PATH="/root/.local/bin:$PATH"  # ✅ Правильно!
```

**Файлы исправлены:**
- `devops/dockerfiles/bot.Dockerfile`
- `devops/dockerfiles/api.Dockerfile`

**Симптом ошибки:**
```
#14 0.577 /bin/sh: 1: uv: not found
#14 ERROR: process "/bin/sh -c uv sync --frozen --no-dev" did not complete successfully: exit code: 127
```

---

### 2. .dockerignore размещен неправильно ❌ → ✅ ИСПРАВЛЕНО

**Проблема:**
- `.dockerignore` был только в `devops/`
- Docker build context находится в корне проекта (из-за `context: ..` в docker-compose.yml)
- Результат: Docker копировал весь `frontend/node_modules/` (~750MB+)

**Решение:**
- Скопирован `.dockerignore` в корень проекта
- Добавлены дополнительные правила:
  ```
  node_modules/
  **/node_modules/
  frontend/node_modules/
  frontend/.next/
  ```

**Симптом ошибки:**
```
[+] Building 78.2s (12/18)
=> ERROR [bot internal] load build context                               72.9s
=> => transferring context: 751.80MB                                     72.9s
failed to solve: failed to checksum file frontend/node_modules/.pnpm/@eslint+config-array@0.21.0/node_modules/@eslint/object-schema: archive/tar: unknown file mode
```

---

### 3. Docker Compose version warning (некритично)

**Предупреждение:**
```
level=warning msg="docker-compose.yml: the attribute `version` is obsolete"
```

**Решение (опционально):**
Удалить `version: '3.9'` из начала `docker-compose.yml` - это устаревший атрибут в Docker Compose v2.

---

## Уроки

1. **Всегда тестировать** - без реального запуска можно упустить критические проблемы
2. **.dockerignore в правильном месте** - должен быть в корне build context, а не в devops/
3. **ENV PATH** - проверять реальное расположение установленных инструментов
4. **node_modules огромные** - обязательно исключать из Docker context

## Файлы обновлены

- ✅ `.dockerignore` (создан в корне проекта)
- ✅ `devops/dockerfiles/bot.Dockerfile` (исправлен PATH)
- ✅ `devops/dockerfiles/api.Dockerfile` (исправлен PATH)

## Статус

После исправлений Docker сборка должна проходить успешно.

---

**Автор**: Обнаружено при первом реальном тестировании
**Важность**: Критическая (без этого Docker не работал вообще)

