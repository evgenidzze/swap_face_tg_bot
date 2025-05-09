import random
import asyncio
from typing import Union
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.exceptions import BadRequest
from aiogram.dispatcher.filters import Text

from keyboards.keyboards import use_avatar_kb
from create_bot import bot
from start_bot import hero_faces
from utils.utils import get_swapped_photo, generate_slots_kb, random_text, create_rega_btn

# In aiogram 2, we don't use Router but Dispatcher
# Router functionality will be integrated in the main script

class FSMClient(StatesGroup):
    user_photo = State()
    slot_name = State()


async def start_handler(message: types.Message, state: FSMContext):
    await state.finish()  # In aiogram 2, we use finish() instead of clear()

    # Extract deep link parameter if any
    args = message.get_args()
    if args:
        if args == 'help':
            from handlers.help import help_handler
            await help_handler(message)
            return
        elif args == 'bonus':
            from handlers.bonus import bonus_handler
            await bonus_handler(message)
            return
        elif args == 'generate':
            await get_bonus_handler(message, state)
            return

    # If no deep link or unknown command, show regular start message
    await message.reply(
        "🎭 <b>CasinoFace — бот, который превращает тебя в героя культовых азартных игр!</b>\n\n"
        "👀 <i>Хочешь узнать, кем бы ты был в мире ставок и больших выигрышей?</i>\n\n"
        "🎁 <b>Загрузи фото — и получи свой образ и БОНУС на игру, в которую ты идеально впишешься!</b>\n\n"
        "⬇️ <i>Просто отправь фото, либо разреши боту использовать твою аватарку — и узнай, на какого героя слота ты похож больше всего!</i>\n\n"
        "⚡️ <b>Убедись, что на фото хорошо видно лицо, иначе бот не сможет создать изображение</b>"
        , parse_mode="HTML"
        , reply_markup=use_avatar_kb)


async def slot_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(slot_name=call.data)
    await FSMClient.user_photo.set()

    await call.message.answer(
        f"🔥 Отличный выбор!\n\n"
        f"Теперь загрузите фото, чтобы примерить образ из слота {call.data.replace('_', ' ').title()}\n\n")


async def user_photo_handler(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❗ <b>Пожалуйста, загрузите фото с лицом</b>")
        return
    loading_gif_buffered = InputFile('static/loading.gif')
    await bot.send_animation(chat_id=message.from_user.id,
                             animation=loading_gif_buffered,
                             caption=(
                                 "⚙️ <b>Загружаем твое альтер-эго...</b>\n\n"
                                 "⏳ <i>Это займет несколько секунд. В это время твоя реальность переплетается с азартом...</i>"
                             ),
                             parse_mode="HTML")

    data = await state.get_data()
    slot_name = data.get('slot_name')
    input_file, slot_name = await get_swapped_photo(message.photo[-1].file_id, slot_name)

    if input_file:
        # In aiogram 2, we create keyboard differently
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='ЗАБРАТЬ ФРИСПИНЫ', callback_data='get_free_spins'))
        kb.add(InlineKeyboardButton(text='ПОПРОБОВАТЬ ЕЩЕ', callback_data='get_bonus'))

        await message.answer_photo(photo=input_file,
                                   caption=f"🔥 <b>БУМ! А вот и ты!\n\n</b>"
                                           f"<i>Узнаешь?! - главный герой игры {slot_name.replace('_', ' ').title()}\n\n</i>"
                                           f"<b>Выглядишь потрясающе!</b>",
                                   parse_mode="HTML")

        await message.answer("🎯 И по традиции, дарим бонус для этой игры\n\n"
                             f"10 бесплатных вращений в игре {slot_name.replace('_', ' ').title()}\n\n"
                             "👇 Жми и забирай", reply_markup=kb, parse_mode="HTML")
        await state.finish()
    else:
        await message.answer("Не удалось обнаружить лицо на фото, попробуйте загрузить другое изображение")


async def use_avatar_handler(message_or_call: Union[types.Message, types.CallbackQuery], state: FSMContext):
    user_id = message_or_call.from_user.id
    loading_gif_buffered = InputFile('static/loading.gif')

    await bot.send_animation(chat_id=user_id,
                             animation=loading_gif_buffered,
                             caption=(
                                 "⚙️ <b>Загружаем твое альтер-эго...</b>\n\n"
                                 "⏳ <i>Это займет несколько секунд. В это время твоя реальность переплетается с азартом...</i>"
                             ),
                             parse_mode="HTML")

    no_avatar_text = (
        "❗ <b>Не удалось обработать ваше фото</b>\n\n"
        "📸 <i>Пожалуйста, отправьте фотографию с лицом, чтобы попробовать снова.</i>"
    )

    if isinstance(message_or_call, types.CallbackQuery):
        await message_or_call.answer()
        photos = await bot.get_user_profile_photos(user_id=user_id)
        file_id = photos.photos[0][-1].file_id if photos.total_count else None
        message = message_or_call.message
    else:
        photos = message_or_call.photo
        file_id = photos[-1].file_id
        message = message_or_call

    if file_id:
        hero_name = random.choice(list(hero_faces.keys()))
        input_file, slot_name = await get_swapped_photo(file_id, hero_name)

        if input_file:
            text = await random_text(slot_name)
            btn = await create_rega_btn(user_id, text="ИГРАТЬ!")
            # In aiogram 2, we need to add buttons to a keyboard
            keyboard = InlineKeyboardMarkup()
            keyboard.add(btn)

            await bot.send_photo(chat_id=user_id,
                                 photo=input_file,
                                 caption=text,
                                 reply_markup=keyboard,
                                 parse_mode="HTML")

            # Only send delayed registration message if it's a callback query (not a direct photo)
            if isinstance(message_or_call, types.CallbackQuery):
                btn = await create_rega_btn(user_id, text="ИГРАТЬ!")
                kb = InlineKeyboardMarkup()
                kb.add(btn)

                asyncio.create_task(send_delayed_message(
                    user_id,
                    delay=20,
                    message_text="💬 <b>И кстати, пока ты здесь, спешу поделиться советом..</b>\n\n"
                                 "🎰 <b>Казино SLOTTICA, кроме фриспинов, ДАРИТ ВСЕМ НОВЫМ ИГРОКАМ +200% на первое пополнение!</b>\n\n"
                                 "⚡️ <i>Не забудь активировать бонус сразу после регистрации.</i>",
                    kb=kb
                ))

            kb = InlineKeyboardMarkup()
            btn = await create_rega_btn(user_id, text="🎰 ЗАБРАТЬ ФРИСПИНЫ 🎰 (рега)")
            kb.add(btn)
            kb.add(InlineKeyboardButton(text='👻 БОЛЬШЕ БОНУСОВ ТУТ 👻', callback_data='bonus'))

            asyncio.create_task(send_delayed_message(
                user_id,
                delay=3,
                message_text="<b>Как и обещали — дарим бонус для этого слота</b>\n\n"
                             "🎁 <b>10 бесплатных вращений в игре [название слота]</b>\n\n"
                             "🏆 <i>Прямо сейчас в этом слоте игрок #45701 поймал множитель х882</i>\n\n"
                             "<b>Попробуй превзойти этот результат!</b> <i>А с бонусом у тебя уже есть фора!</i>\n\n"
                             "👇 👇 <b>Жми и забирай</b>",
                kb=kb
            ))

            await asyncio.sleep(8)
            await get_bonus_handler(message_or_call, state=state)
            return

    # Если не удалось обработать фото или его нет
    if isinstance(message_or_call, types.CallbackQuery):
        await message_or_call.message.answer(no_avatar_text, parse_mode="HTML")
    else:
        await message_or_call.answer(no_avatar_text, parse_mode="HTML")


async def get_free_spins_handler(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='БОНУС 200%', callback_data='get_bonus'))

    await call.message.answer("И кстати, пока ты здесь, спешу поделиться советом..\n\n"
                              "Казино SLOTTICA, кроме фриспинов, ДАРИТ ВСЕМ НОВЫИ ИГРОКАМ +200% на первое пополнение!\n\n"
                              "Не забудь активировать бонус сразу после регистрации"
                              , reply_markup=kb, parse_mode="HTML")


async def get_bonus_handler(event: Union[types.CallbackQuery, types.Message], state: FSMContext):
    await state.finish()  # In aiogram 2, we use finish() instead of clear()
    kb = await generate_slots_kb()
    await FSMClient.slot_name.set()

    user_id = event.from_user.id
    if isinstance(event, types.CallbackQuery):
        message_obj = event.message
    else:
        message_obj = event

    await bot.send_message(user_id,
                           "👑 Хочешь примерить другие образы?\n\n"
                           "Каждое новое перевоплощение = новый бонус!\n\n"
                           "👇 Выбери слот"
                           , reply_markup=kb, parse_mode="HTML")

    btn = await create_rega_btn(user_id, text="БОНУС +200%")
    kb = InlineKeyboardMarkup()
    kb.add(btn)

    asyncio.create_task(send_delayed_message(
        user_id,
        delay=3,
        message_text="💬 <b>И кстати, пока ты здесь, спешу поделиться советом..</b>\n\n"
                     "🎰 <b>Казино SLOTTICA, кроме фриспинов, ДАРИТ ВСЕМ НОВЫМ ИГРОКАМ +200% на первое пополнение!</b>\n\n"
                     "⚡️ <i>Не забудь активировать бонус сразу после регистрации.</i>",
        kb=kb
    ))


async def send_delayed_message(user_id, delay, message_text, kb):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id=user_id,
                           text=message_text,
                           parse_mode="HTML",
                           reply_markup=kb
                           )


def register_handlers(dp: Dispatcher):
    """Register all handlers to dispatcher"""
    dp.register_message_handler(start_handler, commands=['start'], state='*')
    dp.register_message_handler(get_bonus_handler, commands=['generate'], state='*')
    dp.register_callback_query_handler(use_avatar_handler, Text(equals='use_avatar'), state='*')
    dp.register_callback_query_handler(slot_handler, state=FSMClient.slot_name)
    dp.register_message_handler(user_photo_handler, content_types=['photo'], state=FSMClient.user_photo)
    dp.register_message_handler(use_avatar_handler, content_types=['photo'], state='*')
    dp.register_callback_query_handler(get_free_spins_handler, Text('get_free_spins'))
    dp.register_callback_query_handler(get_bonus_handler,  Text('get_bonus'))
