"""Скрипт для создания тестовых данных в БД для тестирования Dashboard и Chat"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Добавляем родительскую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from services.database import close_db, get_pool, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def create_test_data() -> None:
    """Создать тестовые данные в БД"""

    logger.info("Инициализация подключения к БД...")
    await init_db()

    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # Проверяем, есть ли уже данные
            await cur.execute("SELECT COUNT(*) FROM users")
            user_count = (await cur.fetchone())[0]

            if user_count > 0:
                logger.info(f"В БД уже есть {user_count} пользователей")
                response = input("Создать дополнительные тестовые данные? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Отменено пользователем")
                    return

            logger.info("Создание тестовых данных...")

            # Создаем 10 тестовых пользователей
            user_ids = []
            for i in range(1, 11):
                await cur.execute(
                    """
                    INSERT INTO users (telegram_user_id, first_name, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (telegram_user_id) DO NOTHING
                    RETURNING id
                    """,
                    (1000 + i, f"TestUser{i}", datetime.now() - timedelta(days=60 - i*5))
                )
                result = await cur.fetchone()
                if result:
                    user_ids.append(result[0])
                    logger.info(f"Создан пользователь TestUser{i}")

            # Создаем 10 тестовых чатов
            chat_ids = []
            for i in range(1, 11):
                await cur.execute(
                    """
                    INSERT INTO chats (telegram_chat_id, created_at)
                    VALUES (%s, %s)
                    ON CONFLICT (telegram_chat_id) DO NOTHING
                    RETURNING id
                    """,
                    (2000 + i, datetime.now() - timedelta(days=60 - i*5))
                )
                result = await cur.fetchone()
                if result:
                    chat_ids.append(result[0])
                    logger.info(f"Создан чат {2000 + i}")

            # Создаем сообщения за последние 90 дней
            logger.info("Создание тестовых сообщений...")
            message_count = 0

            for day in range(90):
                current_date = datetime.now() - timedelta(days=90 - day)

                # Количество сообщений в день варьируется
                # Будние дни больше, выходные меньше
                is_weekend = current_date.weekday() >= 5
                base_messages = 10 if is_weekend else 30

                messages_per_day = base_messages + (day % 5) * 2

                for msg in range(messages_per_day):
                    # Выбираем случайного пользователя и чат
                    user_id = user_ids[msg % len(user_ids)]
                    chat_id = chat_ids[msg % len(chat_ids)]

                    # Чередуем роли
                    role = 'user' if msg % 2 == 0 else 'assistant'

                    # Генерируем контент разной длины
                    content = f"Test message {message_count}: " + "Lorem ipsum " * (msg % 10 + 1)
                    length = len(content)

                    await cur.execute(
                        """
                        INSERT INTO messages (user_id, chat_id, role, content, length, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (user_id, chat_id, role, content, length, current_date)
                    )
                    message_count += 1

                if day % 10 == 0:
                    logger.info(f"Создано сообщений: {message_count}")

            logger.info("✅ Успешно создано:")
            logger.info(f"  - Пользователей: {len(user_ids)}")
            logger.info(f"  - Чатов: {len(chat_ids)}")
            logger.info(f"  - Сообщений: {message_count}")

            # Показываем статистику
            await cur.execute("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL")
            total_users = (await cur.fetchone())[0]

            await cur.execute("SELECT COUNT(*) FROM chats WHERE deleted_at IS NULL")
            total_chats = (await cur.fetchone())[0]

            await cur.execute("SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL")
            total_messages = (await cur.fetchone())[0]

            await cur.execute("SELECT AVG(length) FROM messages WHERE deleted_at IS NULL")
            avg_length = (await cur.fetchone())[0]

            logger.info("\n📊 Текущая статистика в БД:")
            logger.info(f"  - Всего пользователей: {total_users}")
            logger.info(f"  - Всего чатов: {total_chats}")
            logger.info(f"  - Всего сообщений: {total_messages}")
            logger.info(f"  - Средняя длина сообщения: {avg_length:.1f}")

    await close_db()
    logger.info("✅ Готово!")


async def clear_test_data() -> None:
    """Очистить тестовые данные"""

    logger.warning("⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные из БД!")
    response = input("Вы уверены? Введите 'DELETE' для подтверждения: ")

    if response != 'DELETE':
        logger.info("Отменено")
        return

    logger.info("Инициализация подключения к БД...")
    await init_db()

    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            logger.info("Удаление всех данных...")

            await cur.execute("DELETE FROM messages")
            await cur.execute("DELETE FROM chats")
            await cur.execute("DELETE FROM users")

            logger.info("✅ Все данные удалены")

    await close_db()


async def main() -> None:
    """Главная функция"""

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        await clear_test_data()
    else:
        try:
            config = load_config()
            logger.info(f"Подключение к БД: {config.database_url.split('@')[1]}")
            await create_test_data()
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            sys.exit(1)


if __name__ == "__main__":
    # Fix for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

