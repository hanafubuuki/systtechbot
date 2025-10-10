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
    chat_id = message.chat.id
    
    logger.info(f"User {user_id} started conversation: user_name={user_name}, chat_id={chat_id}")
    
    await message.answer(
        f"👋 Привет, {user_name}!\n\n"
        f"Я — AI-ассистент, готов помочь тебе.\n"
        f"Просто напиши мне что-нибудь, и я отвечу!"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help - справка по командам"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    logger.info(f"User {user_id} requested help: chat_id={chat_id}")
    
    help_text = (
        "📖 Доступные команды:\n\n"
        "/start - Начать общение с ботом\n"
        "/help - Показать эту справку\n"
        "/clear - Очистить историю диалога\n\n"
        "💬 Просто напиши мне сообщение, и я отвечу!"
    )
    
    await message.answer(help_text)


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

