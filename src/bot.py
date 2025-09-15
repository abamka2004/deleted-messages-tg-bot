import logging
from uuid import uuid4

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from src.config import get_token, get_user_id
from src.db.models import MessageLog
from src.db.database import async_session
from src.keyboards import get_event_markup

from sqlalchemy import select

logger = logging.getLogger(__name__)

bot = Bot(get_token())
dp = Dispatcher()

USER_ID = get_user_id()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    logger.info(f"Start command received from user {message.from_user.id}")
    await message.answer("<b>Инструкция по активации бота:</b>\n\n"
                         "<blockquote>"
                         f"1. Скопируйте юз Вашего бота\n"
                         "2. Перейдите в: Настройки > Telegram для бизнеса > Чат-боты\n"
                         "3. Вставьте в поле 'Ссылка или @имя_бота' скопированный юз"
                         "</blockquote>\n\n"
                         "<b>Готово!</b>",
                         parse_mode="HTML")


@dp.business_message()
async def handle_business_message(message: types.Message):
    async with async_session() as db:
        try:
            logger.info(f"New business message from user {message.from_user.id} in chat {message.chat.id}")
            log_entry = MessageLog(
                id=uuid4(),
                chat_id=message.chat.id,
                message_id=message.message_id,
                original_text=message.text or "",
                from_user_id=message.from_user.id,
                event_type="created"
            )
            db.add(log_entry)
            await db.commit()
            logger.debug(f"Message {message.message_id} saved to database")
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")


@dp.edited_business_message()
async def handle_edited_business_message(message: types.Message):
    async with async_session() as db:
        try:
            logger.info(f"Edited business message from user {message.from_user.id}")
            result = await db.execute(
                select(MessageLog).where(
                    (MessageLog.chat_id == message.chat.id) &
                    (MessageLog.message_id == message.message_id)
                )
            )
            log_entry: MessageLog = result.scalar_one_or_none()

            if log_entry:
                log_entry.edited_text = message.text
                log_entry.event_type = "edited"
                await db.commit()
                logger.debug(f"Message {message.message_id} updated in database")

                await bot.send_message(
                    chat_id=USER_ID,
                    text=f"✏️ Сообщение отредактировано:\n\n"
                         f"Original: <blockquote>{log_entry.original_text}</blockquote>\n\n"
                         f"Edited: <blockquote>{message.text}</blockquote>",
                    reply_markup=get_event_markup(message.from_user.id)
                )
                logger.info(f"Edit notification sent for message {message.message_id}")
            else:
                logger.warning(f"Original message {message.message_id} not found in database")
        except Exception as e:
            logger.error(f"Error processing edit: {str(e)}")


@dp.deleted_business_messages()
async def handle_deleted_business_messages(event: types.BusinessMessagesDeleted):
    async with async_session() as db:
        try:
            logger.info(f"Deleted business messages in chat {event.chat.id}")
            for message_id in event.message_ids:
                result = await db.execute(
                    select(MessageLog).where(
                        (MessageLog.chat_id == event.chat.id) &
                        (MessageLog.message_id == message_id)
                    )
                )
                log_entry: MessageLog = result.scalar_one_or_none()

                if log_entry:
                    log_entry.event_type = "deleted"
                    log_entry.is_deleted = 1
                    await db.commit()
                    logger.debug(f"Message {message_id} marked as deleted in database")

                    await bot.send_message(
                        chat_id=USER_ID,
                        text=f"🗑️ Сообщение удалено:\n\n"
                             f"<blockquote>{log_entry.original_text}</blockquote>",
                        reply_markup=get_event_markup(log_entry.from_user_id)
                    )
                    logger.info(f"Delete notification sent for message {message_id}")
                else:
                    logger.warning(f"Message {message_id} not found in database")
        except Exception as e:
            logger.error(f"Error processing deletion: {str(e)}")


@dp.callback_query(F.data == "close_notification")
async def close_notification(callback: types.CallbackQuery):
    logger.info(f"Close notification callback from user {callback.from_user.id}")
    await callback.message.delete()
    await callback.answer()
    logger.debug("Notification message deleted")
