"""Обработчики текстовых сообщений"""
import logging
from aiogram import Router
from aiogram.types import Message

from config import load_config
from services.llm import get_llm_response
from roles.prompts import get_system_prompt

logger = logging.getLogger(__name__)
router = Router()

# Загружаем конфигурацию один раз
config = load_config()


@router.message()
async def handle_message(message: Message):
    """Обработчик всех текстовых сообщений (кроме команд)"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_message = message.text
    
    logger.info(f"User {user_id} sent message")
    
    # Формируем контекст для LLM
    messages = [
        {"role": "system", "content": get_system_prompt(user_name)},
        {"role": "user", "content": user_message}
    ]
    
    # Получаем ответ от LLM
    try:
        # Показываем, что бот печатает
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        response = await get_llm_response(messages, config)
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.answer("❌ Произошла ошибка при обработке сообщения.")

