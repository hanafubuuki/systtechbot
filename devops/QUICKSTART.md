# 🚀 Docker Quickstart

Самый быстрый способ запустить все сервисы systtechbot.

## Быстрый старт (3 команды)

```bash
# 1. Перейти в devops директорию
cd devops

# 2. Настроить переменные окружения
cp env.example .env
# Отредактируйте .env и заполните TELEGRAM_TOKEN и OPENAI_API_KEY

# 3. Запустить все сервисы
docker-compose up
```

## Что запустится?

После выполнения команды запустятся 4 сервиса:

- **PostgreSQL** (localhost:5432) - база данных
- **Bot** - Telegram бот (работает в фоне)
- **API** (localhost:8000) - REST API для статистики
- **Frontend** (localhost:3000) - веб-интерфейс

## Проверка работы

1. **Frontend**: Откройте http://localhost:3000
2. **API**: Откройте http://localhost:8000/docs
3. **Bot**: Отправьте `/start` в Telegram боту

## Остановка

```bash
# Ctrl+C в терминале или:
docker-compose down
```

## Подробная документация

Полная документация: [devops/README.md](README.md)

## Устранение проблем

**Порты заняты?** Измените порты в docker-compose.yml

**Ошибки БД?** Проверьте логи:
```bash
docker-compose logs postgres
```

**Нужна помощь?** См. [devops/README.md](README.md) раздел "Устранение проблем"

