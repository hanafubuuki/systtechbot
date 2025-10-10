"""Сервис для работы с LLM через OpenAI-совместимое API"""
import logging
from openai import AsyncOpenAI

from config import Config

logger = logging.getLogger(__name__)


async def get_llm_response(messages: list, config: Config) -> str:
    """
    Получить ответ от LLM
    
    Args:
        messages: Список сообщений в формате OpenAI
        config: Конфигурация приложения
        
    Returns:
        Текст ответа от LLM
    """
    try:
        client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
        
        logger.info(f"LLM request: model={config.openai_model}, messages_count={len(messages)}")
        
        response = await client.chat.completions.create(
            model=config.openai_model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.openai_timeout
        )
        
        # Проверка на пустой ответ
        if not response.choices or not response.choices[0].message.content:
            logger.warning("Empty response from LLM")
            return "🤔 Получен пустой ответ от модели. Попробуйте еще раз."
        
        answer = response.choices[0].message.content
        
        # Очистка от служебных токенов модели
        if answer:
            # Удаляем служебные токены DeepSeek и других моделей
            tokens_to_remove = [
                '<｜begin▁of▁sentence｜>',
                '<|begin_of_sentence|>',
                '<｜end▁of▁sentence｜>',
                '<|end_of_sentence|>',
                '<｜end▁of▁text｜>',
                '<|end_of_text|>',
            ]
            
            for token in tokens_to_remove:
                answer = answer.replace(token, '')
            
            # Убираем лишние пробелы в конце
            answer = answer.strip()
        
        logger.info(f"LLM response: length={len(answer)}")
        
        return answer
        
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"LLM error: {error_type} - {str(e)}")
        
        # Обработка разных типов ошибок
        if "rate" in str(e).lower() or "429" in str(e):
            return "⚠️ Слишком много запросов. Попробуйте через минуту."
        elif "timeout" in str(e).lower():
            return "⏱️ Превышено время ожидания ответа."
        elif "connection" in str(e).lower():
            return "❌ Не удалось подключиться к сервису."
        else:
            return "❌ Произошла ошибка при обработке запроса."

