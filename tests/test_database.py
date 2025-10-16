"""Тесты для Data Access Layer (database.py)"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.asyncio
async def test_get_or_create_user_new():
    """Тест создания нового пользователя"""
    from services.database import get_or_create_user

    # Mock для pool и connection
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    # Настройка мок cursor
    mock_cursor.fetchone = AsyncMock(return_value={"id": 42})
    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock()

    # Настройка mock connection
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()

    # Настройка mock pool
    mock_pool.connection = MagicMock(return_value=mock_conn)

    with patch("services.database.get_pool", return_value=mock_pool):
        result = await get_or_create_user(123456, "John")

    assert result == 42
    mock_cursor.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_chat():
    """Тест создания чата"""
    from services.database import get_or_create_chat

    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    mock_cursor.fetchone = AsyncMock(return_value={"id": 100})
    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock()

    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()

    mock_pool.connection = MagicMock(return_value=mock_conn)

    with patch("services.database.get_pool", return_value=mock_pool):
        result = await get_or_create_chat(789012)

    assert result == 100
    mock_cursor.execute.assert_called_once()


@pytest.mark.asyncio
async def test_save_message():
    """Тест сохранения сообщения"""
    from services.database import save_message

    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    mock_cursor.fetchone = AsyncMock(return_value={"id": 999})
    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock()

    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()

    mock_pool.connection = MagicMock(return_value=mock_conn)

    with patch("services.database.get_pool", return_value=mock_pool):
        result = await save_message(1, 2, "user", "Hello world")

    assert result == 999
    # Проверяем что execute был вызван с правильными параметрами
    call_args = mock_cursor.execute.call_args
    assert "Hello world" in str(call_args)
    assert 11 in call_args[0][1]  # length = len("Hello world") = 11


@pytest.mark.asyncio
async def test_get_messages_empty():
    """Тест получения пустого списка сообщений"""
    from services.database import get_messages

    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    mock_cursor.fetchall = AsyncMock(return_value=[])
    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock()

    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()

    mock_pool.connection = MagicMock(return_value=mock_conn)

    with patch("services.database.get_pool", return_value=mock_pool):
        result = await get_messages(1, 2, limit=10)

    assert result == []
    mock_cursor.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_messages_with_data():
    """Тест получения сообщений из БД"""
    from services.database import get_messages

    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    # Мокируем результаты (в обратном порядке, так как сортировка DESC)
    mock_rows = [
        {"id": 2, "role": "assistant", "content": "Hi!", "length": 3},
        {"id": 1, "role": "user", "content": "Hello", "length": 5},
    ]
    mock_cursor.fetchall = AsyncMock(return_value=mock_rows)
    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock()

    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()

    mock_pool.connection = MagicMock(return_value=mock_conn)

    with patch("services.database.get_pool", return_value=mock_pool):
        result = await get_messages(1, 2, limit=10)

    # Должны вернуться в прямом порядке (старое -> новое)
    assert len(result) == 2
    assert result[0]["content"] == "Hello"
    assert result[1]["content"] == "Hi!"


@pytest.mark.asyncio
async def test_soft_delete_messages():
    """Тест soft delete сообщений"""
    from services.database import soft_delete_messages

    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock()

    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock()

    mock_pool.connection = MagicMock(return_value=mock_conn)

    with patch("services.database.get_pool", return_value=mock_pool):
        await soft_delete_messages(1, 2)

    # Проверяем что UPDATE был вызван
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args
    assert "UPDATE messages" in str(call_args)
    assert "deleted_at" in str(call_args)
