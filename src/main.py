import asyncio
import logging

from src.bot import bot, dp
from src.db.database import init_models
from src.sheduler import scheduler

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting scheduler initialization")

    await scheduler.start_auto_clear_db()

    logger.info("Starting bot initialization")

    try:
        # Инициализация БД
        await init_models()
        logger.info("Database initialized successfully")

        # Запуск бота с нужными обработчиками
        logger.info("Starting bot polling")
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "edited_message",
                "business_message",
                "edited_business_message",
                "deleted_business_messages",
                "callback_query"
            ]
        )
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        raise
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
