from datetime import datetime
import logging

from apscheduler.job import Job
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy import delete

from dateutil.relativedelta import relativedelta
import pytz

from src.db.database import async_session
from src.db.models import MessageLog

logger = logging.getLogger(__name__)


class SchedulerManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        self.job: Job | None = None

    async def start_auto_clear_db(self):
        if self.job:
            return  # Уже запущено

        # Запускаем очистку ежедневно в полночь
        self.job = self.scheduler.add_job(self._cleanup_db, 'cron', hour=0)

        try:
            self.scheduler.start()
        except SchedulerAlreadyRunningError:
            pass

        logger.info("Automatic database cleanup is running")

    @staticmethod
    async def _cleanup_db():
        try:
            async with async_session() as session:
                # Вычисляем дату, старше которой сообщения будут удаляться
                time_ago = datetime.now(pytz.timezone("Europe/Moscow")) - relativedelta(days=7)

                # Создаем запрос на удаление
                result = await session.execute(
                    delete(MessageLog).where(MessageLog.timestamp < time_ago)
                )

                await session.commit()

                logger.info(f"Deleted {result.rowcount} messages older than {time_ago}")

        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
            await session.rollback()


scheduler = SchedulerManager()
