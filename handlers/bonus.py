from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text

from utils.utils import get_rega

# In aiogram 2, we create keyboards differently and register handlers directly to Dispatcher

async def bonus_handler(message: types.Message):
    # Create keyboard manually in aiogram 2
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text='К ИГРАМ', url='https://google.com'))
    kb.add(InlineKeyboardButton(text='Применить образ', callback_data='get_bonus'))

    rega = await get_rega(message.from_user.id)
    await message.answer(
        "Вам доступны такие бонусы:\n\n"
        f"✅ <b>10 фри спинов Big Bass Bonanza</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️\n\n"
        f"✅ <b>20 фри спинов Pearl Diver</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️\n\n"
        f"❌ <b>20 фри спинов Fire Joker</b>  ➡️ <a href='{rega}'><b>[РАЗБЛОКИРОВАТЬ]</b></a> ⬅️\n\n"
        f"✅ <b>20 фри спинов Dog House</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️\n\n"
        f"❌ <b>20 фри спинов Gates of Olympus</b>  ➡️ <a href='{rega}'><b>[РАЗБЛОКИРОВАТЬ]</b></a> ⬅️\n\n"
        f"✅ <b>+200% на первое пополнение</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️"
        , reply_markup=kb, parse_mode="HTML")

def register_bonus_handlers(dp: Dispatcher):
    # Register command handler
    dp.register_message_handler(bonus_handler, commands=['bonus'], state='*')

    # Register callback query handler for 'bonus' button
    dp.register_callback_query_handler(
        lambda c: bonus_callback_handler(c),
        lambda c: c.data == 'bonus'
    )

async def bonus_callback_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Answer the callback query
    await bonus_handler(callback_query.message)  # Process the message