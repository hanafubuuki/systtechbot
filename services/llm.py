"""Сервис для работы с LLM через OpenAI-совместимое API"""
import logging
import re
from openai import AsyncOpenAI, APIStatusError, APIConnectionError, RateLimitError, APITimeoutError

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
            
            # Удаляем markdown форматирование
            # Удаляем ** для жирного текста
            answer = answer.replace('**', '')
            # Удаляем одинарные * для курсива (но только окружающие слова)
            answer = re.sub(r'\*([^\*]+)\*', r'\1', answer)
            # Удаляем _ для курсива
            answer = re.sub(r'_([^_]+)_', r'\1', answer)
            # Удаляем ` для кода
            answer = answer.replace('`', '')
            
            # Убираем лишние пробелы в конце
            answer = answer.strip()
        
        logger.info(f"LLM response: length={len(answer)}")
        
        return answer
        
    except RateLimitError:
        logger.error("LLM error: RateLimitError - Too many requests")
        return "⚠️ Слишком много запросов. Попробуйте через минуту."
    except APITimeoutError:
        logger.error("LLM error: APITimeoutError - Request timed out")
        return "⏱️ Превышено время ожидания ответа."
    except APIConnectionError as e:
        logger.error(f"LLM error: APIConnectionError - {e}")
        return "❌ Не удалось подключиться к сервису. Проверьте ваше интернет-соединение или URL."
    except APIStatusError as e:
        logger.error(f"LLM error: APIStatusError - {e.status_code} - {e.response}")
        if e.status_code == 404:
            return "❌ Модель не найдена или недоступна. Проверьте название модели."
        return f"❌ Ошибка сервиса LLM: {e.status_code}. Попробуйте позже."
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"LLM error: {error_type} - {str(e)}")
        return "❌ Произошла непредвиденная ошибка при обработке запроса."

