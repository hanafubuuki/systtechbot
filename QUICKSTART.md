# ⚡ Шпаргалка по запуску бота

## 🚀 Быстрый запуск

### 1️⃣ Запустить все с нуля
```powershell
# Запустить PostgreSQL
docker-compose up -d

# Подождать 5 секунд для инициализации
Start-Sleep -Seconds 5

# Запустить бота (в фоне)
Start-Process powershell -ArgumentList "uv run bot.py" -NoNewWindow

# ИЛИ запустить бота в текущем окне (видны логи)
uv run bot.py
```

### 2️⃣ Через Makefile (быстрее)
```powershell
make db-up      # Запустить PostgreSQL
make run        # Запустить бота
```

---

## 🛑 Остановка бота

### Способ 1: Через Ctrl+C
Если бот запущен в текущем окне терминала - просто нажмите `Ctrl+C`

### Способ 2: Убить все процессы Python
```powershell
taskkill /F /IM python.exe
```

### Способ 3: Через Process ID (если знаете PID)
```powershell
# Найти процесс
Get-Process python

# Остановить по ID
Stop-Process -Id <PID>
```

---

## 🔄 Перезапуск

### Полный перезапуск системы
```powershell
# Остановить все
taskkill /F /IM python.exe
docker-compose down

# Запустить все заново
docker-compose up -d
Start-Sleep -Seconds 5
uv run bot.py
```

### Перезапуск только бота (БД не трогаем)
```powershell
taskkill /F /IM python.exe
Start-Sleep -Seconds 2
uv run bot.py
```

---

## 📊 Проверка статуса

### Проверить что запущено
```powershell
# PostgreSQL
docker ps --filter "name=systtechbot_postgres"

# Бот
Get-Process python -ErrorAction SilentlyContinue
```

### Просмотр логов
```powershell
# Последние 20 строк
Get-Content bot.log -Tail 20

# В реальном времени (live)
Get-Content bot.log -Wait -Tail 20

# Только ошибки
Get-Content bot.log | Select-String "ERROR"
```

---

## 🗄️ Работа с базой данных

### Подключиться к БД
```powershell
docker exec -it systtechbot_postgres psql -U systtechbot -d systtechbot
```

### Быстрые запросы (без входа в psql)
```powershell
# Посмотреть все таблицы
docker exec systtechbot_postgres psql -U systtechbot -d systtechbot -c "\dt"

# Посмотреть пользователей
docker exec systtechbot_postgres psql -U systtechbot -d systtechbot -c "SELECT * FROM users;"

# Посмотреть последние 5 сообщений
docker exec systtechbot_postgres psql -U systtechbot -d systtechbot -c "SELECT id, role, LEFT(content, 50) as content, created_at FROM messages ORDER BY created_at DESC LIMIT 5;"

# Статистика
docker exec systtechbot_postgres psql -U systtechbot -d systtechbot -c "SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL;"
```

---

## 🧹 Очистка и сброс

### Очистить логи
```powershell
Remove-Item bot.log -Force
```

### Сбросить базу данных (ОСТОРОЖНО!)
```powershell
make db-reset   # Удалит все данные и применит миграции заново
```

### Полная очистка
```powershell
# Остановить все
taskkill /F /IM python.exe
docker-compose down -v  # -v удаляет volumes (данные БД)

# Запустить с чистого листа
docker-compose up -d
Start-Sleep -Seconds 5
uv run alembic upgrade head
uv run bot.py
```

---

## 🐛 Устранение проблем

### Ошибка: "Conflict: terminated by other getUpdates"
**Причина:** Запущено несколько экземпляров бота
**Решение:**
```powershell
taskkill /F /IM python.exe
Start-Sleep -Seconds 3
uv run bot.py
```

### Ошибка: "port is already allocated" (порт 5432 занят)
**Причина:** Уже запущен другой PostgreSQL
**Решение:**
```powershell
# Остановить другие PostgreSQL контейнеры
docker ps | findstr postgres
docker stop <container_name>

# Или остановить все Docker контейнеры
docker stop $(docker ps -q)
```

### Ошибка: "DATABASE_URL не установлен"
**Причина:** Отсутствует `.env` файл
**Решение:**
```powershell
# Создать .env из примера
copy .env.example .env

# Отредактировать токены
notepad .env
```

### БД не подключается
```powershell
# Проверить что PostgreSQL запущен
docker ps --filter "name=systtechbot_postgres"

# Посмотреть логи PostgreSQL
docker logs systtechbot_postgres

# Перезапустить PostgreSQL
docker-compose restart
```

---

## 📝 Полезные алиасы (добавить в PowerShell Profile)

```powershell
# Открыть профиль для редактирования
notepad $PROFILE

# Добавить эти функции:
function bot-start { docker-compose up -d; Start-Sleep 5; uv run bot.py }
function bot-stop { taskkill /F /IM python.exe }
function bot-restart { bot-stop; Start-Sleep 2; bot-start }
function bot-logs { Get-Content bot.log -Wait -Tail 20 }
function bot-status { docker ps --filter "name=systtechbot"; Get-Process python -ErrorAction SilentlyContinue }
function db-shell { docker exec -it systtechbot_postgres psql -U systtechbot -d systtechbot }

# Использование после перезапуска PowerShell:
# bot-start
# bot-logs
# bot-status
# db-shell
```

---

## 🎯 Типичный рабочий процесс

### Начало работы
```powershell
cd c:\zz\systtechbot
docker-compose up -d
Start-Sleep 5
uv run bot.py
```

### Конец работы
```powershell
# Нажать Ctrl+C (если бот в текущем окне)
# ИЛИ
taskkill /F /IM python.exe
docker-compose down
```

### Быстрый тест
```powershell
# Открыть бота в Telegram: @mzakharovsysttech_bot
# Отправить: /start
# Отправить: Привет!
# Проверить логи: Get-Content bot.log -Tail 10
```

---

## 📞 Контакты

- **Бот:** [@mzakharovsysttech_bot](https://t.me/mzakharovsysttech_bot)
- **Документация:** `doc/guides/`
- **Ручное тестирование:** `doc/guides/MANUAL_TESTING.md`

---

**Версия:** 0.1.0 (MVP)
**Дата обновления:** 2025-10-16

