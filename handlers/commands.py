"""Обработчики команд бота"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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

