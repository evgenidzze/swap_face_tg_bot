from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

use_avatar_kb = InlineKeyboardMarkup()
use_avatar_kb.add(InlineKeyboardButton(text="Использовать аватарку 🖼", callback_data="use_avatar"))

