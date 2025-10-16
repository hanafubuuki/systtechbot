"""Обработчики команд бота"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from roles.prompts import ROLE_INFO
from services.context import clear_context

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start"""
    if not message.from_user:
        return

    user_name = message.from_user.first_name if message.from_user.first_name else "друг"
    user_id = message.from_user.id
    chat_id = message.chat.id

    logger.info(f"User {user_id} started conversation in chat {chat_id}")

    welcome_text = f"""Привет, {user_name}! 👋

Я — AI-ассистент, готовый помочь вам с различными вопросами.

Просто напишите мне сообщение, и я постараюсь помочь!

Используйте /help для списка доступных команд."""

    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help"""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested help")

    help_text = """📖 Доступные команды:

/start - Начать общение
/help - Показать эту справку
/clear - Очистить историю
/role - Показать информацию о роли бота

💬 Просто напишите мне сообщение, и я отвечу!"""

    await message.answer(help_text)


@router.message(Command("clear"))
async def cmd_clear(message: Message) -> None:
    """Обработчик команды /clear"""
    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    await clear_context(user_id, chat_id)
    logger.info(f"User {user_id} cleared context in chat {chat_id}")

    await message.answer("🗑️ История диалога очищена!")


@router.message(Command("role"))
async def cmd_role(message: Message) -> None:
    """Обработчик команды /role - показать информацию о роли бота"""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested role info")

    await message.answer(ROLE_INFO)
