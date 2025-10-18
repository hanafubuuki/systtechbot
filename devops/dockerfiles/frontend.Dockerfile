# Базовый образ Node.js 20
FROM node:20-alpine

# Установка pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Установка зависимостей
RUN pnpm install --frozen-lockfile

# Копирование исходного кода frontend
COPY frontend/ .

# Сборка приложения
RUN pnpm build

# Expose порт Next.js
EXPOSE 3000

# Запуск продакшн сервера
CMD ["pnpm", "start"]

