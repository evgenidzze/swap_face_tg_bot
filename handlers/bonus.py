from aiogram import types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command('bonus'))
async def bonus_handler(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text='К ИГРАМ', url='https://google.com')
    kb.button(text='Применить образ', callback_data='get_bonus')
    kb.adjust(1)
    await message.answer(
        "Вам доступны такие бонусы:\n\n"
        "✅ 10 фри спинов Big bass bonanza"
        "  ⬆️ [ЗАБРАТЬ] ⬆️\n\n"


        "✅ 20 фри спинов Pearl Diver"
        "  ⬆️ [ЗАБРАТЬ] ⬆️\n\n"


        "❌ 20 фри спинов Fire Joker"
        "  ⬆️ [РАЗБЛОКИРОВАТЬ] ⬆️\n\n"

        "✅ 20 фри спинов Dog House"
        "  ⬆️ [ЗАБРАТЬ] ⬆️\n\n"

        "❌ 20 фри спинов Gates of Olympus"
        "  ⬆️ [РАЗБЛОКИРОВАТЬ] ⬆️\n\n"

        "✅ +200% на первое пополнение"
        "  ⬆️ [ЗАБРАТЬ] ⬆️"

        , reply_markup=kb.as_markup())
