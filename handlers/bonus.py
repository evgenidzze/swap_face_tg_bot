from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils import get_rega

router = Router()

@router.message(F.data == 'bonus')
@router.message(Command('bonus'), StateFilter('*'))
async def bonus_handler(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text='К ИГРАМ', url='https://google.com')
    kb.button(text='Применить образ', callback_data='get_bonus')
    kb.adjust(1)
    rega = await get_rega(message.from_user.id)
    await message.answer(
        "Вам доступны такие бонусы:\n\n"
        f"✅ <b>10 фри спинов Big Bass Bonanza</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️ (рега)\n\n"
        f"✅ <b>20 фри спинов Pearl Diver</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️ (рега)\n\n"
        f"❌ <b>20 фри спинов Fire Joker</b>  ➡️ <a href='{rega}'><b>[РАЗБЛОКИРОВАТЬ]</b></a> ⬅️ (рега)\n\n"
        f"✅ <b>20 фри спинов Dog House</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️ (рега)\n\n"
        f"❌ <b>20 фри спинов Gates of Olympus</b>  ➡️ <a href='{rega}'><b>[РАЗБЛОКИРОВАТЬ]</b></a> ⬅️ (рега)\n\n"
        f"✅ <b>+200% на первое пополнение</b>  ➡️ <a href='{rega}'><b>[ЗАБРАТЬ]</b></a> ⬅️ (рега)"
        , reply_markup=kb.as_markup(), parse_mode="HTML")
