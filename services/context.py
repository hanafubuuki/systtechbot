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
    user_id: int,
    chat_id: int,
    messages: list[Message],
    user_name: str | None = None,
    max_context_messages: int = 15,
) -> None:
    """
    Сохранить контекст пользователя в БД с автоматической очисткой старых сообщений

    Args:
        user_id: ID пользователя в Telegram
        chat_id: ID чата в Telegram
        messages: Список сообщений в формате OpenAI
        user_name: Имя пользователя (опционально)
        max_context_messages: Максимальное количество сообщений для хранения
    """
    # Получить или создать пользователя и чат
    db_user_id = await get_or_create_user(user_id, user_name or "Unknown")
    db_chat_id = await get_or_create_chat(chat_id)

    # Получить существующие сообщения
    existing_messages = await get_messages(db_user_id, db_chat_id, limit=200)
    existing_count = len(existing_messages)

    # Сохранить только новые сообщения (те, что после existing_count)
    new_messages = messages[existing_count:]
    for msg in new_messages:
        await save_message(db_user_id, db_chat_id, msg["role"], msg["content"])

    # Проверяем общее количество после добавления
    total_count = existing_count + len(new_messages)

    # Если превышен лимит - удаляем самые старые сообщения
    if total_count > max_context_messages:
        # Обновляем список всех сообщений после добавления
        all_messages = await get_messages(db_user_id, db_chat_id, limit=200)

        # Количество сообщений для удаления
        messages_to_delete = len(all_messages) - max_context_messages

        if messages_to_delete > 0:
            # Удаляем самые старые (первые в списке, т.к. они отсортированы по created_at ASC)
            from services.database import get_pool

            pool = await get_pool()
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    # Получаем ID самых старых сообщений
                    ids_to_delete = [msg["id"] for msg in all_messages[:messages_to_delete]]

                    # Soft delete
                    await cur.execute(
                        """
                        UPDATE messages
                        SET deleted_at = NOW()
                        WHERE id = ANY(%s)
                        """,
                        (ids_to_delete,),
                    )
                    await conn.commit()

            logger.info(
                f"Deleted {messages_to_delete} old messages for user {user_id} in chat {chat_id}"
            )

    logger.info(
        f"Context saved for user {user_id} in chat {chat_id}: "
        f"{len(new_messages)} new messages, {min(total_count, max_context_messages)} kept in DB"
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
