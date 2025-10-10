.PHONY: help install run test clean

help:
	@echo "Доступные команды:"
	@echo "  make install  - Установить зависимости через uv"
	@echo "  make run      - Запустить бота"
	@echo "  make test     - Запустить тесты"
	@echo "  make clean    - Очистить временные файлы"

install:
	@echo "📦 Создание виртуального окружения..."
	uv venv
	@echo "📦 Установка зависимостей..."
	uv sync
	@echo "📝 Создание .env файла..."
	@if not exist .env (copy .env.example .env) else (echo .env уже существует)
	@echo "✅ Готово! Настройте токены в .env и запустите: make run"

run:
	uv run bot.py

test:
	uv run pytest tests/ -v

clean:
	@echo "🧹 Очистка временных файлов..."
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	@if exist bot.log del /f /q bot.log
	@echo "✅ Очистка завершена"

