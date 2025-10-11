"""Тесты для команд бота"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from handlers.commands import cmd_clear, cmd_help, cmd_start


@pytest.fixture
def mock_message():
    """Создает mock объект Message от aiogram"""
    message = MagicMock()
    message.from_user.id = 12345
    message.from_user.first_name = "Иван"
    message.chat.id = 67890
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_cmd_start_with_user_name(mock_message):
    """Тест команды /start с именем пользователя"""
    await cmd_start(mock_message)

    # Проверяем, что ответ был отправлен
    mock_message.answer.assert_called_once()

    # Проверяем содержимое ответа
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет, Иван!" in call_args
    assert "AI-ассистент" in call_args


@pytest.mark.asyncio
async def test_cmd_start_without_user_name(mock_message):
    """Тест команды /start без имени пользователя"""
    mock_message.from_user.first_name = None

    await cmd_start(mock_message)

    # Проверяем, что используется "друг" вместо имени
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет, друг!" in call_args


@pytest.mark.asyncio
async def test_cmd_start_with_empty_name(mock_message):
    """Тест команды /start с пустым именем"""
    mock_message.from_user.first_name = ""

    await cmd_start(mock_message)

    # Проверяем, что используется "друг" для пустого имени
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет, друг!" in call_args


@pytest.mark.asyncio
async def test_cmd_help(mock_message):
    """Тест команды /help"""
    await cmd_help(mock_message)

    # Проверяем, что ответ был отправлен
    mock_message.answer.assert_called_once()

    # Проверяем содержимое справки
    call_args = mock_message.answer.call_args[0][0]
    assert "Доступные команды" in call_args
    assert "/start" in call_args
    assert "/help" in call_args
    assert "/clear" in call_args


@pytest.mark.asyncio
async def test_cmd_help_contains_all_commands(mock_message):
    """Тест что /help содержит все основные команды"""
    await cmd_help(mock_message)

    call_args = mock_message.answer.call_args[0][0]

    # Проверяем что есть все три команды
    assert "/start - Начать общение" in call_args
    assert "/help - Показать эту справку" in call_args
    assert "/clear - Очистить историю" in call_args


@pytest.mark.asyncio
async def test_cmd_clear(mock_message):
    """Тест команды /clear"""
    with patch("handlers.commands.clear_context") as mock_clear:
        await cmd_clear(mock_message)

        # Проверяем, что функция очистки была вызвана с правильными параметрами
        mock_clear.assert_called_once_with(mock_message.from_user.id, mock_message.chat.id)

        # Проверяем, что ответ был отправлен
        mock_message.answer.assert_called_once()

        # Проверяем содержимое ответа
        call_args = mock_message.answer.call_args[0][0]
        assert "История диалога очищена" in call_args


@pytest.mark.asyncio
async def test_cmd_clear_uses_correct_ids(mock_message):
    """Тест что /clear использует правильные user_id и chat_id"""
    mock_message.from_user.id = 99999
    mock_message.chat.id = 11111

    with patch("handlers.commands.clear_context") as mock_clear:
        await cmd_clear(mock_message)

        # Проверяем точные значения
        mock_clear.assert_called_once_with(99999, 11111)


@pytest.mark.asyncio
async def test_all_commands_call_answer(mock_message):
    """Тест что все команды отправляют ответ пользователю"""
    # Тестируем /start
    await cmd_start(mock_message)
    assert mock_message.answer.call_count == 1

    # Сбрасываем счетчик
    mock_message.answer.reset_mock()

    # Тестируем /help
    await cmd_help(mock_message)
    assert mock_message.answer.call_count == 1

    # Сбрасываем счетчик
    mock_message.answer.reset_mock()

    # Тестируем /clear
    with patch("handlers.commands.clear_context"):
        await cmd_clear(mock_message)
        assert mock_message.answer.call_count == 1


@pytest.mark.asyncio
async def test_cmd_start_with_special_characters_in_name(mock_message):
    """Тест /start с спецсимволами в имени пользователя"""
    mock_message.from_user.first_name = "Иван-Петр_123"

    await cmd_start(mock_message)

    call_args = mock_message.answer.call_args[0][0]
    assert "Привет, Иван-Петр_123!" in call_args


@pytest.mark.asyncio
async def test_cmd_help_has_emoji(mock_message):
    """Тест что /help содержит эмодзи для визуальной привлекательности"""
    await cmd_help(mock_message)

    call_args = mock_message.answer.call_args[0][0]
    assert "📖" in call_args or "💬" in call_args
