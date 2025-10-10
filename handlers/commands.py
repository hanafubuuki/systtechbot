"""Обработчики команд бота"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.context import clear_context

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name or "друг"
    user_id = message.from_user.id
    
    logger.info(f"User {user_id} started conversation")
    
    await message.answer(
        f"👋 Привет, {user_name}!\n\n"
        f"Я — AI-ассистент, готов помочь тебе.\n"
        f"Просто напиши мне что-нибудь, и я отвечу!"
    )


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Обработчик команды /clear - очистка истории диалога"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    clear_context(user_id, chat_id)
    logger.info(f"User {user_id} cleared conversation history")
    
    await message.answer(
        "🗑️ История диалога очищена.\n"
        "Начнем с чистого листа!"
    )

