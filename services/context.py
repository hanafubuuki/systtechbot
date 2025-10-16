"""Управление контекстом диалогов через PostgreSQL"""

import logging

from constants import MessageRole
from message_types import Message
from services.database import (
    get_messages,
    get_or_create_chat,
    get_or_create_user,
    save_message,
    soft_delete_messages,
)

logger = logging.getLogger(__name__)


async def get_context(user_id: int, chat_id: int) -> dict:
    """
    Получить контекст пользователя из БД

    Args:
        user_id: ID пользователя в Telegram
        chat_id: ID чата в Telegram

    Returns:
        Словарь с контекстом {"messages": [...]}
    """
    # Получить внутренние ID
    db_user_id = await get_or_create_user(user_id, "Unknown")
    db_chat_id = await get_or_create_chat(chat_id)

    # Получить сообщения из БД
    db_messages = await get_messages(db_user_id, db_chat_id, limit=100)

    # Преобразовать в формат OpenAI
    messages: list[Message] = []
    for msg in db_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    logger.info(f"Context loaded for user {user_id} in chat {chat_id}: {len(messages)} messages")
    return {"messages": messages}


async def save_context(
    user_id: int, chat_id: int, messages: list[Message], user_name: str | None = None
) -> None:
    """
    Сохранить контекст пользователя в БД

    Args:
        user_id: ID пользователя в Telegram
        chat_id: ID чата в Telegram
        messages: Список сообщений в формате OpenAI
        user_name: Имя пользователя (опционально)
    """
    # Получить или создать пользователя и чат
    db_user_id = await get_or_create_user(user_id, user_name or "Unknown")
    db_chat_id = await get_or_create_chat(chat_id)

    # Получить существующие сообщения
    existing_messages = await get_messages(db_user_id, db_chat_id, limit=100)
    existing_count = len(existing_messages)

    # Сохранить только новые сообщения (те, что после existing_count)
    new_messages = messages[existing_count:]
    for msg in new_messages:
        await save_message(db_user_id, db_chat_id, msg["role"], msg["content"])

    logger.info(
        f"Context saved for user {user_id} in chat {chat_id}: "
        f"{len(new_messages)} new messages, {len(messages)} total"
    )


async def clear_context(user_id: int, chat_id: int) -> None:
    """
    Очистить контекст пользователя (soft delete)

    Args:
        user_id: ID пользователя в Telegram
        chat_id: ID чата в Telegram
    """
    # Получить внутренние ID
    db_user_id = await get_or_create_user(user_id, "Unknown")
    db_chat_id = await get_or_create_chat(chat_id)

    # Soft delete сообщений
    await soft_delete_messages(db_user_id, db_chat_id)
    logger.info(f"Context cleared for user {user_id} in chat {chat_id}")


def trim_context(messages: list[Message], max_messages: int = 10) -> list[Message]:
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
