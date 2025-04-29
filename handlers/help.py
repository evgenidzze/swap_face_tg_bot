from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command('help'))
async def help_handler(message: types.Message):
    text = """📩 Нужна помощь? Мы рядом

Наша поддержка поможет, если:

▫️ Бонус не пришёл
▫️ Не знаете, что нажать
▫️ Что-то не работает
▫️ Хочется всё пройти быстро

💬 Просто напишите:
👉 @SupportBot — ответим быстро и по делу.

Или выберите нужный раздел из меню ниже"""
    await message.answer(text)