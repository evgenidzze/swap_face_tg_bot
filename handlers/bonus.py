from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command('bonus'), F.data == 'bonus')
async def bonus_handler(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text='К ИГРАМ', url='https://google.com')
    kb.button(text='Применить образ', callback_data='get_bonus')
    kb.adjust(1)
    await message.answer(
        "Вам доступны такие бонусы:\n\n"
        "✅ <b>10 фри спинов Big Bass Bonanza</b>  ➡️ <b>[ЗАБРАТЬ]</b> ⬅️ (рега)\n\n"
        "✅ <b>20 фри спинов Pearl Diver</b>  ➡️ <b>[ЗАБРАТЬ]</b> ⬅️ (рега)\n\n"
        "❌ <b>20 фри спинов Fire Joker</b>  ➡️ <b>[РАЗБЛОКИРОВАТЬ]</b> ⬅️ (рега)\n\n"
        "✅ <b>20 фри спинов Dog House</b>  ➡️ <b>[ЗАБРАТЬ]</b> ⬅️ (рега)\n\n"
        "❌ <b>20 фри спинов Gates of Olympus</b>  ➡️ <b>[РАЗБЛОКИРОВАТЬ]</b> ⬅️ (рега)\n\n"
        "✅ <b>+200% на первое пополнение</b>  ➡️ <b>[ЗАБРАТЬ]</b> ⬅️ (рега)"
        , reply_markup=kb.as_markup(), parse_mode="HTML")
