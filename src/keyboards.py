from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_event_markup(from_user_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text="👤 User", url=f"tg://user?id={from_user_id}")
    builder.button(text="❌ Close", callback_data="close_notification")

    return builder.adjust(2).as_markup()
