"""Точка входа приложения"""
import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import load_config
from handlers import commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Bot starting...")
    
    # Загрузка конфигурации
    try:
        config = load_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Убедитесь, что файл .env содержит TELEGRAM_TOKEN и OPENAI_API_KEY")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.telegram_token)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(commands.router)
    
    # Запуск бота
    try:
        logger.info("✅ Bot started successfully")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())

