"""Интеграционные тесты для handlers"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import MessageRole
from handlers.messages import handle_message
from services.context import get_context, user_contexts


@pytest.fixture(autouse=True)
def clear_contexts():
    """Очистка контекстов перед каждым тестом"""
    user_contexts.clear()
    yield
    user_contexts.clear()


@pytest.fixture
def mock_message():
    """Создает mock объект Message от aiogram"""
    message = MagicMock()
    message.from_user.id = 12345
    message.from_user.first_name = "Тестовый"
    message.chat.id = 67890
    message.text = "Привет!"
    message.answer = AsyncMock()
    message.bot = MagicMock()
    message.bot.send_chat_action = AsyncMock()
    return message


@pytest.fixture
def mock_config():
    """Mock для конфигурации"""
    config = MagicMock()
    config.telegram_token = "test-token"
    config.openai_api_key = "test-key"
    config.openai_base_url = "https://api.openai.com/v1"
    config.openai_model = "gpt-4o-mini"
    config.max_context_messages = 10
    config.temperature = 0.7
    return config


@pytest.mark.asyncio
async def test_handle_message_creates_initial_context(mock_message, mock_config):
    """Тест создания начального контекста при первом сообщении"""
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content="Привет! Как дела?"))]

    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value="Привет! Как дела?"):
            await handle_message(mock_message)

            # Проверяем, что контекст создан
            context = get_context(mock_message.from_user.id, mock_message.chat.id)
            messages = context.get("messages", [])

            # Должно быть 3 сообщения: system, user, assistant
            assert len(messages) == 3
            assert messages[0]["role"] == MessageRole.SYSTEM
            assert messages[1]["role"] == MessageRole.USER
            assert messages[1]["content"] == "Привет!"
            assert messages[2]["role"] == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_handle_message_preserves_context(mock_message, mock_config):
    """Тест сохранения контекста между сообщениями"""
    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value="Ответ"):
            # Первое сообщение
            mock_message.text = "Сообщение 1"
            await handle_message(mock_message)

            # Второе сообщение
            mock_message.text = "Сообщение 2"
            await handle_message(mock_message)

            # Проверяем контекст
            context = get_context(mock_message.from_user.id, mock_message.chat.id)
            messages = context.get("messages", [])

            # system + (user1 + assistant1) + (user2 + assistant2) = 5
            assert len(messages) == 5
            assert messages[1]["content"] == "Сообщение 1"
            assert messages[3]["content"] == "Сообщение 2"


@pytest.mark.asyncio
async def test_handle_message_sends_typing_action(mock_message, mock_config):
    """Тест отправки typing action"""
    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value="Ответ"):
            await handle_message(mock_message)

            # Проверяем, что typing action был отправлен
            mock_message.bot.send_chat_action.assert_called_once_with(
                mock_message.chat.id, "typing"
            )


@pytest.mark.asyncio
async def test_handle_message_sends_response(mock_message, mock_config):
    """Тест отправки ответа пользователю"""
    test_response = "Это тестовый ответ от бота"

    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value=test_response):
            await handle_message(mock_message)

            # Проверяем, что ответ был отправлен
            mock_message.answer.assert_called_once_with(test_response)


@pytest.mark.asyncio
async def test_handle_message_error_handling(mock_message, mock_config):
    """Тест обработки ошибок"""
    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", side_effect=Exception("Test error")):
            await handle_message(mock_message)

            # Проверяем, что отправлено сообщение об ошибке
            mock_message.answer.assert_called_once()
            error_message = mock_message.answer.call_args[0][0]
            assert "❌" in error_message
            assert "ошибка" in error_message.lower()


@pytest.mark.asyncio
async def test_handle_message_without_from_user(mock_config):
    """Тест обработки сообщения без from_user"""
    message = MagicMock()
    message.from_user = None
    message.bot = MagicMock()
    message.answer = AsyncMock()

    with patch("handlers.messages.load_config", return_value=mock_config):
        await handle_message(message)

        # Функция должна завершиться без ошибок
        # Ответ не должен быть отправлен
        message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_without_bot(mock_config):
    """Тест обработки сообщения без bot"""
    message = MagicMock()
    message.from_user.id = 12345
    message.bot = None
    message.answer = AsyncMock()

    with patch("handlers.messages.load_config", return_value=mock_config):
        await handle_message(message)

        # Функция должна завершиться без ошибок
        # Ответ не должен быть отправлен
        message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_context_trimming(mock_message, mock_config):
    """Тест усечения контекста при превышении лимита"""
    # Устанавливаем маленький лимит
    mock_config.max_context_messages = 2

    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value="Ответ"):
            # Отправляем 5 сообщений
            for i in range(5):
                mock_message.text = f"Сообщение {i + 1}"
                await handle_message(mock_message)

            # Проверяем контекст
            context = get_context(mock_message.from_user.id, mock_message.chat.id)
            messages = context.get("messages", [])

            # system + max 2 последних пары (user+assistant) = 1 + 4 = 5
            # Но trim_context должен оставить только последние 2 сообщения + system
            # system + 2 = 3
            assert len(messages) <= mock_config.max_context_messages + 1
            assert messages[0]["role"] == MessageRole.SYSTEM


@pytest.mark.asyncio
async def test_handle_message_user_name_in_context(mock_message, mock_config):
    """Тест сохранения имени пользователя в контексте"""
    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value="Ответ"):
            await handle_message(mock_message)

            # Проверяем, что имя пользователя сохранено
            context = get_context(mock_message.from_user.id, mock_message.chat.id)
            assert context.get("user_name") == "Тестовый"
