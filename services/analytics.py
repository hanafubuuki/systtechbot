"""Сервис для обработки аналитических запросов с text-to-SQL"""

import logging
import re
from typing import Any

from config import Config
from constants import MessageRole
from message_types import Message
from roles.prompts import ANALYTICS_SYSTEM_PROMPT
from services.database import get_pool
from services.llm import get_llm_response

logger = logging.getLogger(__name__)


async def process_analytics_query(
    user_message: str,
    conversation_history: list[Message],
    config: Config
) -> tuple[str, str | None]:
    """
    Обработать аналитический запрос пользователя

    Процесс:
    1. Отправить запрос в LLM с промптом для text-to-SQL
    2. Извлечь SQL из ответа (если есть)
    3. Выполнить SQL
    4. Отправить результаты обратно в LLM для формирования ответа
    5. Вернуть финальный ответ

    Args:
        user_message: Сообщение пользователя
        conversation_history: История диалога
        config: Конфигурация приложения

    Returns:
        Tuple (ответ LLM, выполненный SQL или None)
    """
    # Добавляем system prompt для аналитики если его нет
    messages = conversation_history.copy()
    if not messages or messages[0]["role"] != MessageRole.SYSTEM:
        messages.insert(0, {"role": MessageRole.SYSTEM, "content": ANALYTICS_SYSTEM_PROMPT})
    else:
        # Заменяем system prompt на аналитический
        messages[0] = {"role": MessageRole.SYSTEM, "content": ANALYTICS_SYSTEM_PROMPT}

    # Обрезаем контекст до MAX_CONTEXT_MESSAGES (оставляем system + последние N сообщений)
    if len(messages) > config.max_context_messages:
        # Сохраняем system prompt и последние (MAX_CONTEXT_MESSAGES - 1) сообщений
        system_prompt = messages[0]
        recent_messages = messages[-(config.max_context_messages - 1):]
        messages = [system_prompt] + recent_messages
        logger.info(f"Context truncated to {len(messages)} messages (was {len(conversation_history)})")

    # Добавляем сообщение пользователя
    messages.append({"role": MessageRole.USER, "content": user_message})

    # Первый запрос к LLM - генерация SQL (если нужно)
    logger.info("Отправка запроса в LLM для генерации SQL...")
    llm_response = await get_llm_response(messages, config)

    # Пытаемся извлечь SQL из ответа
    sql = extract_sql_from_response(llm_response)

    if sql:
        logger.info(f"SQL извлечен из ответа: {sql[:100]}...")

        # Выполняем SQL
        try:
            results = await execute_sql_query(sql)
            logger.info(f"SQL выполнен успешно, получено {len(results)} строк")

            # Форматируем результаты для LLM
            results_text = format_sql_results(results)

            # Добавляем ответ LLM в историю
            messages.append({"role": MessageRole.ASSISTANT, "content": llm_response})

            # Отправляем результаты SQL обратно в LLM для формирования финального ответа
            follow_up_message = (
                f"Результаты запроса к базе данных:\n\n{results_text}\n\n"
                f"ВАЖНО: Сформируй понятный текстовый ответ пользователю на основе этих данных. "
                f"НЕ ВЫВОДИ SQL КОД! Только естественный текст на русском языке."
            )
            messages.append({"role": MessageRole.USER, "content": follow_up_message})

            logger.info("Отправка результатов SQL в LLM для формирования финального ответа...")
            final_response = await get_llm_response(messages, config)

            # Удаляем SQL блоки из финального ответа если они есть
            # (иногда бесплатные модели всё равно их возвращают)
            import re
            final_response = re.sub(r'```sql.*?```', '', final_response, flags=re.DOTALL | re.IGNORECASE)
            final_response = re.sub(r'```.*?```', '', final_response, flags=re.DOTALL)
            final_response = final_response.strip()

            return final_response, sql

        except Exception as e:
            logger.error(f"Ошибка выполнения SQL: {e}")
            error_message = f"Произошла ошибка при выполнении запроса к базе данных: {str(e)}"
            return error_message, sql
    else:
        # SQL не требуется, возвращаем ответ как есть
        logger.info("SQL не требуется для этого запроса")
        return llm_response, None


def extract_sql_from_response(text: str) -> str | None:
    """
    Извлечь SQL запрос из ответа LLM

    Ищет SQL в блоках кода с маркерами ```sql ... ``` или просто SELECT

    Args:
        text: Текст ответа от LLM

    Returns:
        SQL запрос или None если не найден
    """
    # Сначала пытаемся найти блок кода SQL с маркерами
    pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        sql = match.group(1).strip()
        return sql

    # Пытаемся найти блок кода без указания языка
    pattern = r"```\s*(SELECT.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        sql = match.group(1).strip()
        return sql

    # Пытаемся найти SELECT запрос без маркеров (если он занимает значительную часть ответа)
    pattern = r"(SELECT\s+.*?(?:FROM|;).*?)(?:\n\n|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        sql = match.group(1).strip()
        # Проверяем что это похоже на SQL (содержит ключевые слова)
        if any(keyword in sql.upper() for keyword in ['SELECT', 'FROM', 'WHERE']):
            # Убираем точку с запятой в конце если есть
            sql = sql.rstrip(';').strip()
            return sql

    return None


async def execute_sql_query(sql: str) -> list[dict[str, Any]]:
    """
    Выполнить SELECT запрос к базе данных

    Args:
        sql: SQL запрос

    Returns:
        Список словарей с результатами

    Raises:
        ValueError: Если запрос не является SELECT
        Exception: При ошибке выполнения запроса
    """
    # Автоисправление частых ошибок названий колонок (snake_case)
    # Бесплатные LLM часто забывают подчеркивания
    common_fixes = {
        'deletedat': 'deleted_at',
        'createdat': 'created_at',
        'firstname': 'first_name',
        'telegramuserid': 'telegram_user_id',
        'telegramchatid': 'telegram_chat_id',
        'userid': 'user_id',
        'chatid': 'chat_id',
    }

    sql_fixed = sql
    for wrong, correct in common_fixes.items():
        # Заменяем только целые слова (не внутри других слов)
        pattern = r'\b' + wrong + r'\b'
        sql_fixed = re.sub(pattern, correct, sql_fixed, flags=re.IGNORECASE)

    if sql_fixed != sql:
        logger.info(f"Auto-fixed column names in SQL query")
        sql = sql_fixed

    # Проверка безопасности - только SELECT запросы
    sql_lower = sql.lower().strip()
    if not sql_lower.startswith("select"):
        raise ValueError("Разрешены только SELECT запросы")

    # Проверка на опасные операции
    # Используем границы слов: пробелы, скобки, запятые, начало/конец строки
    dangerous_keywords = ["insert", "update", "delete", "drop", "create", "alter", "truncate", "exec", "execute"]

    for keyword in dangerous_keywords:
        # Pattern ищет keyword окруженный границами (не внутри идентификатора)
        # Например, найдет " delete " но не "deleted_at"
        pattern = r'(?:^|[\s(,;])' + re.escape(keyword) + r'(?:[\s),;]|$)'
        if re.search(pattern, sql_lower):
            logger.warning(f"Найдено запрещенное SQL ключевое слово '{keyword}' в запросе")
            raise ValueError(f"Запрос содержит запрещенное ключевое слово: {keyword}")

    logger.info(f"✅ SQL прошел валидацию безопасности")

    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)

            # Получаем названия колонок
            column_names = [desc[0] for desc in cur.description] if cur.description else []

            # Получаем результаты
            rows = await cur.fetchall()

            # Преобразуем в список словарей
            results = []
            for row in rows:
                row_dict = {col: val for col, val in zip(column_names, row)}
                results.append(row_dict)

            return results


def format_sql_results(results: list[dict[str, Any]], max_rows: int = 50) -> str:
    """
    Форматировать результаты SQL для отправки в LLM

    Args:
        results: Список словарей с результатами
        max_rows: Максимальное количество строк для отображения

    Returns:
        Отформатированная строка с результатами
    """
    if not results:
        return "Запрос не вернул результатов."

    # Ограничиваем количество строк
    limited_results = results[:max_rows]

    # Формируем текстовое представление
    lines = []
    lines.append(f"Количество строк: {len(results)}")

    if len(results) > max_rows:
        lines.append(f"(Показано первых {max_rows} из {len(results)})")

    lines.append("")

    # Добавляем данные
    for i, row in enumerate(limited_results, 1):
        lines.append(f"Строка {i}:")
        for key, value in row.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    return "\n".join(lines)

