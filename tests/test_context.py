"""Тесты для управления контекстом диалогов"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import MessageRole
from services.context import clear_context, get_context, save_context, trim_context


@pytest.mark.asyncio
async def test_get_context_empty():
    """Тест получения пустого контекста"""
    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=1)),
        patch("services.context.get_or_create_chat", new=AsyncMock(return_value=1)),
        patch("services.context.get_messages", new=AsyncMock(return_value=[])),
    ):
        result = await get_context(123, 456)

    assert result == {"messages": []}


@pytest.mark.asyncio
async def test_save_and_get_context():
    """Тест сохранения и получения контекста"""
    user_id = 123
    chat_id = 456
    messages = [
        {"role": MessageRole.SYSTEM, "content": "System prompt"},
        {"role": MessageRole.USER, "content": "Hello"},
        {"role": MessageRole.ASSISTANT, "content": "Hi there!"},
    ]
    user_name = "Ivan"

    # Mock для get_messages возвращает те же сообщения
    db_messages = [
        {"id": 1, "role": "system", "content": "System prompt"},
        {"id": 2, "role": "user", "content": "Hello"},
        {"id": 3, "role": "assistant", "content": "Hi there!"},
    ]

    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=1)),
        patch("services.context.get_or_create_chat", new=AsyncMock(return_value=1)),
        patch("services.context.save_message", new=AsyncMock()),
        patch("services.context.get_messages", new=AsyncMock(return_value=db_messages)),
    ):
        # Сохраняем контекст
        await save_context(user_id, chat_id, messages, user_name)

        # Получаем контекст
        result = await get_context(user_id, chat_id)

    assert result["messages"] == messages


@pytest.mark.asyncio
async def test_save_context_without_name():
    """Тест сохранения контекста без имени пользователя"""
    user_id = 789
    chat_id = 101
    messages = [{"role": MessageRole.USER, "content": "Test"}]

    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=1)),
        patch("services.context.get_or_create_chat", new=AsyncMock(return_value=1)),
        patch("services.context.save_message", new=AsyncMock()),
        patch("services.context.get_messages", new=AsyncMock(return_value=[])),
    ):
        await save_context(user_id, chat_id, messages)

    # Тест прошел успешно если не было exception


@pytest.mark.asyncio
async def test_clear_context():
    """Тест очистки контекста"""
    user_id = 111
    chat_id = 222

    mock_soft_delete = AsyncMock()

    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=1)),
        patch("services.context.get_or_create_chat", new=AsyncMock(return_value=1)),
        patch("services.context.soft_delete_messages", new=mock_soft_delete),
    ):
        await clear_context(user_id, chat_id)

    # Проверяем что soft_delete_messages был вызван
    mock_soft_delete.assert_called_once_with(1, 1)


@pytest.mark.asyncio
async def test_clear_nonexistent_context():
    """Тест очистки несуществующего контекста (не должно падать)"""
    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=1)),
        patch("services.context.get_or_create_chat", new=AsyncMock(return_value=1)),
        patch("services.context.soft_delete_messages", new=AsyncMock()),
    ):
        # Очищаем контекст, которого нет - не должно упасть
        await clear_context(999, 888)

    # Тест прошел успешно если не было exception


def test_trim_context_keeps_system_prompt():
    """Тест усечения контекста - system prompt всегда сохраняется"""
    messages = [
        {"role": MessageRole.SYSTEM, "content": "System prompt"},
        *[{"role": MessageRole.USER, "content": f"Message {i}"} for i in range(20)],
    ]

    result = trim_context(messages, max_messages=5)

    # Должен остаться system prompt + 5 последних сообщений
    assert len(result) == 6
    assert result[0]["role"] == MessageRole.SYSTEM
    assert result[0]["content"] == "System prompt"
    assert result[-1]["content"] == "Message 19"


def test_trim_context_no_trimming_needed():
    """Тест усечения когда сообщений меньше лимита"""
    messages = [
        {"role": MessageRole.SYSTEM, "content": "System"},
        {"role": MessageRole.USER, "content": "Hello"},
        {"role": MessageRole.ASSISTANT, "content": "Hi"},
    ]

    result = trim_context(messages, max_messages=10)

    # Все сообщения должны остаться
    assert len(result) == 3
    assert result == messages


def test_trim_context_empty():
    """Тест усечения пустого контекста"""
    messages = []

    result = trim_context(messages, max_messages=10)

    assert result == []


def test_trim_context_exact_limit():
    """Тест усечения при точном соответствии лимиту"""
    messages = [
        {"role": MessageRole.SYSTEM, "content": "System"},
        *[{"role": MessageRole.USER, "content": f"Msg {i}"} for i in range(10)],
    ]

    result = trim_context(messages, max_messages=10)

    # Должно быть 11 сообщений (system + 10)
    assert len(result) == 11
    assert result == messages


@pytest.mark.parametrize(
    "messages_count,max_messages,expected_count,description",
    [
        (5, 10, 5, "меньше лимита"),
        (11, 10, 11, "равно лимиту + system"),
        (25, 10, 11, "больше лимита"),
        (3, 20, 3, "лимит больше количества"),
        (15, 5, 6, "усечение до 5 + system"),
    ],
)
def test_trim_context_parametrized(messages_count, max_messages, expected_count, description):
    """Параметризованный тест усечения контекста"""
    # Создаем messages_count сообщений (включая system)
    messages = [{"role": MessageRole.SYSTEM, "content": "System"}]
    messages += [
        {"role": MessageRole.USER, "content": f"Message {i}"} for i in range(messages_count - 1)
    ]

    result = trim_context(messages, max_messages)

    assert len(result) == expected_count, f"Fail for case: {description}"
    # System prompt всегда первый
    if result:
        assert result[0]["role"] == MessageRole.SYSTEM


@pytest.mark.asyncio
async def test_multiple_users_separate_contexts():
    """Тест раздельных контекстов для разных пользователей"""

    # Разные user_id возвращают разные db_user_id
    async def mock_get_or_create_user(telegram_user_id: int, name: str):  # type: ignore[misc]
        return telegram_user_id  # Просто возвращаем telegram_user_id как db_user_id

    # Mock messages для разных пользователей
    async def mock_get_messages(user_id: int, chat_id: int, limit: int = 10):  # type: ignore[misc]
        if user_id == 1:
            return [{"id": 1, "role": "user", "content": "User 1"}]
        elif user_id == 2:
            return [{"id": 2, "role": "user", "content": "User 2"}]
        return []

    with (
        patch("services.context.get_or_create_user", new=mock_get_or_create_user),
        patch(
            "services.context.get_or_create_chat",
            new=AsyncMock(side_effect=[100, 200, 100, 200]),
        ),
        patch("services.context.get_messages", new=mock_get_messages),
        patch("services.context.save_message", new=AsyncMock()),
    ):
        # Сохраняем для пользователей
        await save_context(1, 100, [{"role": MessageRole.USER, "content": "User 1"}], "Alice")
        await save_context(2, 200, [{"role": MessageRole.USER, "content": "User 2"}], "Bob")

        # Получаем контексты
        context1 = await get_context(1, 100)
        context2 = await get_context(2, 200)

    assert context1["messages"][0]["content"] == "User 1"
    assert context2["messages"][0]["content"] == "User 2"


@pytest.mark.asyncio
async def test_same_user_different_chats():
    """Тест разных контекстов для одного пользователя в разных чатах"""

    # Mock messages для разных чатов
    async def mock_get_messages(user_id: int, chat_id: int, limit: int = 10):  # type: ignore[misc]
        if chat_id == 1:
            return [{"id": 1, "role": "user", "content": "Chat 1"}]
        elif chat_id == 2:
            return [{"id": 2, "role": "user", "content": "Chat 2"}]
        return []

    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=100)),
        patch("services.context.get_or_create_chat", new=AsyncMock(side_effect=[1, 2, 1, 2])),
        patch("services.context.get_messages", new=mock_get_messages),
        patch("services.context.save_message", new=AsyncMock()),
    ):
        # Сохраняем для разных чатов
        await save_context(100, 1, [{"role": MessageRole.USER, "content": "Chat 1"}])
        await save_context(100, 2, [{"role": MessageRole.USER, "content": "Chat 2"}])

        # Получаем контексты
        context1 = await get_context(100, 1)
        context2 = await get_context(100, 2)

    assert context1["messages"][0]["content"] == "Chat 1"
    assert context2["messages"][0]["content"] == "Chat 2"


@pytest.mark.asyncio
async def test_context_update():
    """Тест обновления существующего контекста"""
    user_id = 500
    chat_id = 600

    # Первый вызов get_messages возвращает 1 сообщение, второй - 2
    get_messages_calls = [
        [],  # Первый save_context
        [{"id": 1, "role": "user", "content": "First"}],  # Второй save_context
        [  # get_context
            {"id": 1, "role": "user", "content": "First"},
            {"id": 2, "role": "assistant", "content": "Response"},
        ],
    ]

    with (
        patch("services.context.get_or_create_user", new=AsyncMock(return_value=1)),
        patch("services.context.get_or_create_chat", new=AsyncMock(return_value=1)),
        patch("services.context.get_messages", new=AsyncMock(side_effect=get_messages_calls)),
        patch("services.context.save_message", new=AsyncMock()),
    ):
        # Первое сохранение
        await save_context(user_id, chat_id, [{"role": MessageRole.USER, "content": "First"}])

        # Обновление контекста
        new_messages = [
            {"role": MessageRole.USER, "content": "First"},
            {"role": MessageRole.ASSISTANT, "content": "Response"},
        ]
        await save_context(user_id, chat_id, new_messages, "Updated User")

        # Получаем обновленный контекст
        result = await get_context(user_id, chat_id)

    assert len(result["messages"]) == 2
