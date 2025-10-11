"""Тесты для управления контекстом диалогов"""

import sys
from pathlib import Path

import pytest

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import MessageRole
from services.context import clear_context, get_context, save_context, trim_context, user_contexts


def test_get_context_empty():
    """Тест получения пустого контекста"""
    # Очищаем глобальное хранилище перед тестом
    user_contexts.clear()

    result = get_context(123, 456)

    assert result == {"messages": []}
    assert "user_name" not in result
    assert "last_activity" not in result


def test_save_and_get_context():
    """Тест сохранения и получения контекста"""
    user_contexts.clear()

    user_id = 123
    chat_id = 456
    messages = [
        {"role": MessageRole.SYSTEM, "content": "System prompt"},
        {"role": MessageRole.USER, "content": "Hello"},
        {"role": MessageRole.ASSISTANT, "content": "Hi there!"},
    ]
    user_name = "Ivan"

    # Сохраняем контекст
    save_context(user_id, chat_id, messages, user_name)

    # Получаем контекст
    result = get_context(user_id, chat_id)

    assert result["messages"] == messages
    assert result["user_name"] == user_name
    assert "last_activity" in result


def test_save_context_without_name():
    """Тест сохранения контекста без имени пользователя"""
    user_contexts.clear()

    user_id = 789
    chat_id = 101
    messages = [{"role": MessageRole.USER, "content": "Test"}]

    save_context(user_id, chat_id, messages)

    result = get_context(user_id, chat_id)
    assert result["messages"] == messages
    assert result["user_name"] is None


def test_clear_context():
    """Тест очистки контекста"""
    user_contexts.clear()

    user_id = 111
    chat_id = 222
    messages = [{"role": MessageRole.USER, "content": "Test message"}]

    # Сохраняем контекст
    save_context(user_id, chat_id, messages, "Test User")

    # Проверяем что контекст существует
    assert get_context(user_id, chat_id)["messages"] == messages

    # Очищаем контекст
    clear_context(user_id, chat_id)

    # Проверяем что контекст пуст
    assert get_context(user_id, chat_id) == {"messages": []}


def test_clear_nonexistent_context():
    """Тест очистки несуществующего контекста (не должно падать)"""
    user_contexts.clear()

    # Очищаем контекст, которого нет
    clear_context(999, 888)

    # Проверяем что ничего не сломалось
    assert get_context(999, 888) == {"messages": []}


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


def test_multiple_users_separate_contexts():
    """Тест раздельных контекстов для разных пользователей"""
    user_contexts.clear()

    # Пользователь 1
    save_context(1, 100, [{"role": MessageRole.USER, "content": "User 1"}], "Alice")

    # Пользователь 2
    save_context(2, 200, [{"role": MessageRole.USER, "content": "User 2"}], "Bob")

    # Проверяем что контексты разные
    context1 = get_context(1, 100)
    context2 = get_context(2, 200)

    assert context1["messages"][0]["content"] == "User 1"
    assert context1["user_name"] == "Alice"

    assert context2["messages"][0]["content"] == "User 2"
    assert context2["user_name"] == "Bob"


def test_same_user_different_chats():
    """Тест разных контекстов для одного пользователя в разных чатах"""
    user_contexts.clear()

    user_id = 100

    # Чат 1
    save_context(user_id, 1, [{"role": MessageRole.USER, "content": "Chat 1"}])

    # Чат 2
    save_context(user_id, 2, [{"role": MessageRole.USER, "content": "Chat 2"}])

    # Проверяем что контексты разные
    context1 = get_context(user_id, 1)
    context2 = get_context(user_id, 2)

    assert context1["messages"][0]["content"] == "Chat 1"
    assert context2["messages"][0]["content"] == "Chat 2"


def test_context_update():
    """Тест обновления существующего контекста"""
    user_contexts.clear()

    user_id = 500
    chat_id = 600

    # Первое сохранение
    save_context(user_id, chat_id, [{"role": MessageRole.USER, "content": "First"}])

    # Обновление контекста
    new_messages = [
        {"role": MessageRole.USER, "content": "First"},
        {"role": MessageRole.ASSISTANT, "content": "Response"},
    ]
    save_context(user_id, chat_id, new_messages, "Updated User")

    # Проверяем обновленный контекст
    result = get_context(user_id, chat_id)

    assert len(result["messages"]) == 2
    assert result["user_name"] == "Updated User"
