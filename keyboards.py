from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

use_avatar_kb = InlineKeyboardBuilder()
use_avatar_kb.button(text="Использовать аватарку", callback_data="use_avatar")
