import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import get_db_url
from src.db.models import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(get_db_url(), echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_models():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database models initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database models: {str(e)}")
        raise


def async_session():
    logger.debug("Creating new database session")
    return AsyncSessionLocal()
