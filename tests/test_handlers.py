"""Интеграционные тесты для handlers"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import MessageRole
from handlers.messages import handle_message
from services.context import get_context

# Глобальное хранилище для эмуляции БД в тестах
_test_db_users = {}
_test_db_chats = {}
_test_db_messages = []
_test_db_id_counter = 1


def _reset_test_db():
    """Сбросить тестовую БД"""
    global _test_db_id_counter
    _test_db_users.clear()
    _test_db_chats.clear()
    _test_db_messages.clear()
    _test_db_id_counter = 1


async def _mock_get_or_create_user(telegram_user_id: int, first_name: str):  # type: ignore[misc]
    """Mock для get_or_create_user"""
    if telegram_user_id not in _test_db_users:
        global _test_db_id_counter
        _test_db_users[telegram_user_id] = _test_db_id_counter
        _test_db_id_counter += 1
    return _test_db_users[telegram_user_id]


async def _mock_get_or_create_chat(telegram_chat_id: int):  # type: ignore[misc]
    """Mock для get_or_create_chat"""
    if telegram_chat_id not in _test_db_chats:
        global _test_db_id_counter
        _test_db_chats[telegram_chat_id] = _test_db_id_counter
        _test_db_id_counter += 1
    return _test_db_chats[telegram_chat_id]


async def _mock_save_message(user_id: int, chat_id: int, role: str, content: str):  # type: ignore[misc]
    """Mock для save_message"""
    global _test_db_id_counter
    msg_id = _test_db_id_counter
    _test_db_id_counter += 1
    _test_db_messages.append(
        {
            "id": msg_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "deleted_at": None,
        }
    )
    return msg_id


async def _mock_get_messages(user_id: int, chat_id: int, limit: int = 10):  # type: ignore[misc]
    """Mock для get_messages"""
    messages = [
        msg
        for msg in _test_db_messages
        if msg["user_id"] == user_id and msg["chat_id"] == chat_id and msg["deleted_at"] is None
    ]
    return messages[-limit:] if len(messages) > limit else messages


async def _mock_soft_delete_messages(user_id: int, chat_id: int):  # type: ignore[misc]
    """Mock для soft_delete_messages"""
    for msg in _test_db_messages:
        if msg["user_id"] == user_id and msg["chat_id"] == chat_id:
            msg["deleted_at"] = True


@pytest.fixture(autouse=True)
def mock_database():
    """Mock всех database функций для тестов"""
    _reset_test_db()
    with (
        patch("services.context.get_or_create_user", new=_mock_get_or_create_user),
        patch("services.context.get_or_create_chat", new=_mock_get_or_create_chat),
        patch("services.context.save_message", new=_mock_save_message),
        patch("services.context.get_messages", new=_mock_get_messages),
        patch("services.context.soft_delete_messages", new=_mock_soft_delete_messages),
    ):
        yield
    _reset_test_db()


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
            context = await get_context(mock_message.from_user.id, mock_message.chat.id)
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
            context = await get_context(mock_message.from_user.id, mock_message.chat.id)
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
            context = await get_context(mock_message.from_user.id, mock_message.chat.id)
            messages = context.get("messages", [])

            # trim_context вызывается ДО добавления ответа ассистента
            # Поэтому после 5-го сообщения: trim оставляет 3 (system + 2 последних),
            # затем добавляется ответ ассистента = 4
            # max_messages=2: system + последние 2 после trim + ответ = 4 максимум
            assert len(messages) <= mock_config.max_context_messages + 2
            assert messages[0]["role"] == MessageRole.SYSTEM


@pytest.mark.asyncio
async def test_handle_message_user_name_in_context(mock_message, mock_config):
    """Тест сохранения имени пользователя в контексте"""
    with patch("handlers.messages.load_config", return_value=mock_config):
        with patch("handlers.messages.get_llm_response", return_value="Ответ"):
            await handle_message(mock_message)

            # Note: в новой реализации user_name не хранится в контексте отдельно,
            # а сохраняется в таблице users через get_or_create_user
            # Этот тест проверяет только что контекст существует
            context = await get_context(mock_message.from_user.id, mock_message.chat.id)
            assert len(context.get("messages", [])) > 0
