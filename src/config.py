import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def get_token() -> str:
    token = os.getenv("TOKEN")
    if not token:
        logger.error("TOKEN not found in environment variables")
        raise ValueError("TOKEN environment variable is required")
    logger.info("Token loaded successfully")
    return token


def get_db_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not found in environment variables")
        raise ValueError("DATABASE_URL environment variable is required")
    logger.info("Database URL loaded successfully")
    return db_url


def get_user_id() -> int:
    user_id = os.getenv("USER_ID")
    if not user_id:
        logger.error("USER_ID not found in environment variables")
        raise ValueError("USER_ID environment variable is required")
    try:
        user_id_int = int(user_id)
        logger.info(f"User ID loaded successfully: {user_id_int}")
        return user_id_int
    except ValueError:
        logger.error(f"Invalid USER_ID format: {user_id}")
        raise ValueError("USER_ID must be a valid integer")
