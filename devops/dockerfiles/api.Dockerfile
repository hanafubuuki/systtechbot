# Базовый образ Python 3.11
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка UV для управления зависимостей
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей (включая api опциональные)
RUN uv sync --frozen --no-dev --extra api

# Копирование исходного кода
COPY . .

# Копирование и настройка entrypoint скрипта
COPY devops/scripts/api-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose порт API
EXPOSE 8000

# Запуск через entrypoint скрипт
ENTRYPOINT ["/entrypoint.sh"]

