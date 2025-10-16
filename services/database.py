"""Data Access Layer для работы с PostgreSQL через raw SQL"""

import logging
from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from config import load_config

logger = logging.getLogger(__name__)

# Singleton connection pool
_pool: AsyncConnectionPool | None = None


async def get_pool() -> AsyncConnectionPool:
    """
    Получить connection pool (singleton pattern)

    Returns:
        AsyncConnectionPool instance
    """
    global _pool
    if _pool is None:
        config = load_config()
        logger.info(f"Creating database connection pool to {config.database_url.split('@')[1]}")
        _pool = AsyncConnectionPool(
            conninfo=config.database_url,
            min_size=1,
            max_size=10,
            timeout=30,
        )
    return _pool


async def init_db() -> None:
    """
    Инициализация подключения к БД.
    Проверяет доступность БД.
    """
    try:
        pool = await get_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def close_db() -> None:
    """Закрыть connection pool"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


# ===== Users =====


async def get_or_create_user(telegram_user_id: int, first_name: str) -> int:
    """
    Получить или создать пользователя

    Args:
        telegram_user_id: ID пользователя в Telegram
        first_name: Имя пользователя

    Returns:
        ID пользователя в БД
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO users (telegram_user_id, first_name)
                VALUES (%s, %s)
                ON CONFLICT (telegram_user_id)
                DO UPDATE SET first_name = EXCLUDED.first_name
                RETURNING id
                """,
                (telegram_user_id, first_name),
            )
            result = await cur.fetchone()
            if result is None:
                raise RuntimeError(f"Failed to get or create user {telegram_user_id}")
            user_id: int = result["id"]
            logger.debug(f"User {telegram_user_id} -> DB ID {user_id}")
            return user_id


async def get_user_by_telegram_id(telegram_user_id: int) -> dict[str, Any] | None:
    """
    Получить пользователя по Telegram ID

    Args:
        telegram_user_id: ID пользователя в Telegram

    Returns:
        Словарь с данными пользователя или None
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id, telegram_user_id, first_name, created_at, deleted_at
                FROM users
                WHERE telegram_user_id = %s AND deleted_at IS NULL
                """,
                (telegram_user_id,),
            )
            result = await cur.fetchone()
            return dict(result) if result else None


# ===== Chats =====


async def get_or_create_chat(telegram_chat_id: int) -> int:
    """
    Получить или создать чат

    Args:
        telegram_chat_id: ID чата в Telegram

    Returns:
        ID чата в БД
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO chats (telegram_chat_id)
                VALUES (%s)
                ON CONFLICT (telegram_chat_id)
                DO UPDATE SET telegram_chat_id = EXCLUDED.telegram_chat_id
                RETURNING id
                """,
                (telegram_chat_id,),
            )
            result = await cur.fetchone()
            if result is None:
                raise RuntimeError(f"Failed to get or create chat {telegram_chat_id}")
            chat_id: int = result["id"]
            logger.debug(f"Chat {telegram_chat_id} -> DB ID {chat_id}")
            return chat_id


async def get_chat_by_telegram_id(telegram_chat_id: int) -> dict[str, Any] | None:
    """
    Получить чат по Telegram ID

    Args:
        telegram_chat_id: ID чата в Telegram

    Returns:
        Словарь с данными чата или None
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id, telegram_chat_id, created_at, deleted_at
                FROM chats
                WHERE telegram_chat_id = %s AND deleted_at IS NULL
                """,
                (telegram_chat_id,),
            )
            result = await cur.fetchone()
            return dict(result) if result else None


# ===== Messages =====


async def save_message(user_id: int, chat_id: int, role: str, content: str) -> int:
    """
    Сохранить сообщение в БД

    Args:
        user_id: ID пользователя (внутренний)
        chat_id: ID чата (внутренний)
        role: Роль (system/user/assistant)
        content: Текст сообщения

    Returns:
        ID созданного сообщения
    """
    pool = await get_pool()
    length = len(content)

    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO messages (user_id, chat_id, role, content, length)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, chat_id, role, content, length),
            )
            result = await cur.fetchone()
            if result is None:
                raise RuntimeError("Failed to save message")
            message_id: int = result["id"]
            logger.debug(
                f"Saved message: user={user_id}, chat={chat_id}, role={role}, length={length}"
            )
            return message_id


async def get_messages(user_id: int, chat_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """
    Получить последние сообщения диалога

    Args:
        user_id: ID пользователя (внутренний)
        chat_id: ID чата (внутренний)
        limit: Максимальное количество сообщений

    Returns:
        Список сообщений (от старых к новым)
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id, user_id, chat_id, role, content, length, created_at
                FROM messages
                WHERE user_id = %s AND chat_id = %s AND deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, chat_id, limit),
            )
            results = await cur.fetchall()
            # Reverse to get chronological order (old to new)
            messages = [dict(row) for row in reversed(results)]
            logger.debug(f"Retrieved {len(messages)} messages for user={user_id}, chat={chat_id}")
            return messages


async def soft_delete_messages(user_id: int, chat_id: int) -> None:
    """
    Soft delete всех сообщений диалога

    Args:
        user_id: ID пользователя (внутренний)
        chat_id: ID чата (внутренний)
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE messages
                SET deleted_at = NOW()
                WHERE user_id = %s AND chat_id = %s AND deleted_at IS NULL
                """,
                (user_id, chat_id),
            )
            logger.info(f"Soft deleted messages for user={user_id}, chat={chat_id}")
