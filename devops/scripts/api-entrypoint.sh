#!/bin/bash
# Entrypoint скрипт для API контейнера

set -e

echo "🔄 Waiting for PostgreSQL to be ready..."

# Ждем готовности PostgreSQL
while ! PGPASSWORD=$POSTGRES_PASSWORD psql -h "postgres" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "⏳ PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Запускаем миграции
echo "🔄 Running database migrations..."
cd /app
.venv/bin/alembic upgrade head
echo "✅ Migrations completed!"

# Запускаем API
echo "🚀 Starting API server..."
exec .venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000

