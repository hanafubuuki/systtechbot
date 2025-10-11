"""Обработчики текстовых сообщений"""

import logging

from aiogram import Router
from aiogram.types import Message

from config import load_config
from roles.prompts import get_system_prompt
from services.context import get_context, save_context, trim_context
from services.llm import get_llm_response

logger = logging.getLogger(__name__)
router = Router()

# Загружаем конфигурацию один раз
config = load_config()


@router.message()
async def handle_message(message: Message):
    """Обработчик всех текстовых сообщений (кроме команд)"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_message = message.text

    logger.info(
        f"User {user_id} sent message: length={len(user_message) if user_message else 0}, chat_id={chat_id}"
    )

    # Получаем существующий контекст
    context = get_context(user_id, chat_id)
    messages = context.get("messages", [])

    # Если контекста нет, создаем с system prompt
    if not messages:
        messages = [{"role": "system", "content": get_system_prompt(user_name)}]

    # Добавляем сообщение пользователя
    messages.append({"role": "user", "content": user_message})

    # Усекаем контекст если нужно
    messages = trim_context(messages, max_messages=config.max_context_messages)

    # Получаем ответ от LLM
    try:
        # Показываем, что бот печатает
        await message.bot.send_chat_action(chat_id, "typing")

        response = await get_llm_response(messages, config)

        # Добавляем ответ в контекст
        messages.append({"role": "assistant", "content": response})

        # Сохраняем обновленный контекст
        save_context(user_id, chat_id, messages, user_name)

        await message.answer(response)

        logger.info(
            f"User {user_id} received response: length={len(response)}, context_size={len(messages)}"
        )

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.answer("❌ Произошла ошибка при обработке сообщения.")
