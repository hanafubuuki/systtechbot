.PHONY: help install run test clean format lint typecheck coverage quality

help:
	@echo "Доступные команды:"
	@echo "  make install   - Установить зависимости через uv"
	@echo "  make run       - Запустить бота"
	@echo "  make test      - Запустить тесты"
	@echo "  make format    - Форматировать код (ruff)"
	@echo "  make lint      - Проверить линтером (ruff)"
	@echo "  make typecheck - Проверить типы (mypy)"
	@echo "  make coverage  - Тесты с покрытием"
	@echo "  make quality   - Полная проверка качества"
	@echo "  make clean     - Очистить временные файлы"

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

format:
	@echo "🎨 Форматирование кода..."
	uv run ruff format .
	@echo "✅ Форматирование завершено"

lint:
	@echo "🔍 Проверка линтером..."
	uv run ruff check .
	@echo "✅ Линтер завершен"

typecheck:
	@echo "🔎 Проверка типов..."
	uv run mypy bot.py handlers/ services/ roles/ config.py
	@echo "✅ Проверка типов завершена"

coverage:
	@echo "📊 Запуск тестов с покрытием..."
	uv run pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report: htmlcov/index.html"

quality: format lint typecheck test
	@echo "✅ Все проверки качества пройдены!"

clean:
	@echo "🧹 Очистка временных файлов..."
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	@if exist bot.log del /f /q bot.log
	@if exist .coverage del /f /q .coverage
	@if exist htmlcov rd /s /q htmlcov
	@echo "✅ Очистка завершена"


