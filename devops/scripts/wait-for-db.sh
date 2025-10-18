#!/bin/bash
# Скрипт для ожидания готовности PostgreSQL и запуска миграций

set -e

host="$1"
shift
port="$1"
shift
cmd="$@"

echo "⏳ Ожидание готовности PostgreSQL на $host:$port..."

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -p "$port" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL недоступен - ожидание..."
  sleep 2
done

>&2 echo "✅ PostgreSQL готов!"

# Запуск миграций
echo "🔄 Запуск миграций базы данных..."
alembic upgrade head

echo "✅ Миграции успешно применены!"

# Запуск основной команды
exec $cmd

