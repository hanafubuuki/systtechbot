"""Управление контекстом диалогов"""

import logging
from datetime import datetime

from constants import MessageRole

logger = logging.getLogger(__name__)

# Глобальное хранилище контекстов
# Ключ: (user_id, chat_id)
# Значение: {"messages": [...], "user_name": str, "last_activity": datetime}
user_contexts = {}


def get_context(user_id: int, chat_id: int) -> dict:
    """
    Получить контекст пользователя

    Args:
        user_id: ID пользователя
        chat_id: ID чата

    Returns:
        Словарь с контекстом или пустой словарь
    """
    key = (user_id, chat_id)
    return user_contexts.get(key, {"messages": []})


def save_context(user_id: int, chat_id: int, messages: list, user_name: str = None):
    """
    Сохранить контекст пользователя

    Args:
        user_id: ID пользователя
        chat_id: ID чата
        messages: Список сообщений в формате OpenAI
        user_name: Имя пользователя (опционально)
    """
    key = (user_id, chat_id)
    user_contexts[key] = {
        "messages": messages,
        "user_name": user_name,
        "last_activity": datetime.now(),
    }
    logger.info(
        f"Context saved for user {user_id} in chat {chat_id}, messages count: {len(messages)}"
    )


def clear_context(user_id: int, chat_id: int):
    """
    Очистить контекст пользователя

    Args:
        user_id: ID пользователя
        chat_id: ID чата
    """
    key = (user_id, chat_id)
    if key in user_contexts:
        del user_contexts[key]
        logger.info(f"Context cleared for user {user_id} in chat {chat_id}")


def trim_context(messages: list, max_messages: int = 10) -> list:
    """
    Усечь контекст до максимального количества сообщений
    Всегда сохраняет system prompt (первое сообщение)

    Args:
        messages: Список сообщений
        max_messages: Максимальное количество сообщений (не считая system)

    Returns:
        Усеченный список сообщений
    """
    if not messages:
        return messages

    # Если сообщений меньше или равно лимиту (+1 для system prompt)
    if len(messages) <= max_messages + 1:
        return messages

    # Сохраняем system prompt + последние max_messages сообщений
    system_prompt = messages[0] if messages[0]["role"] == MessageRole.SYSTEM else None
    recent_messages = messages[-(max_messages):]

    if system_prompt:
        return [system_prompt] + recent_messages

    return recent_messages
