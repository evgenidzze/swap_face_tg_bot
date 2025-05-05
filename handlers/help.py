from aiogram import types, Dispatcher

# In aiogram 2, we don't use Router but register handlers directly to Dispatcher

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

def register_help_handlers(dp: Dispatcher):
    dp.register_message_handler(help_handler, commands=['help'])