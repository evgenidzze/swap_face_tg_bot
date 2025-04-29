import random
import asyncio
from typing import Union
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, F, Router

from keyboards import use_avatar_kb
from start_bot import bot, loading_gif_buffered, hero_faces
from utils import get_swapped_photo, generate_slots_kb, random_text, get_rega, create_rega_btn

router = Router()


class FSMClient(StatesGroup):
    user_photo = State()
    slot_name = State()


@router.message(CommandStart())
@router.message(CommandStart(deep_link=True))
async def start_handler(message: types.Message, command: CommandObject, state: FSMContext):
    # Check for deep link parameter
    start_param = command.args
    if start_param:
        if start_param == 'help':
            from handlers.help import help_handler
            await help_handler(message)
            return
        elif start_param == 'bonus':
            from handlers.bonus import bonus_handler
            await bonus_handler(message)
            return
        elif start_param == 'generate':
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
        , reply_markup=use_avatar_kb.as_markup())


@router.callback_query(FSMClient.slot_name)
async def slot_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(slot_name=callback.data)
    await state.set_state(FSMClient.user_photo)
    photos = await bot.get_user_profile_photos(user_id=callback.from_user.id)
    if photos.total_count:
        input_file, slot_name = await get_swapped_photo(photos.photos[0][-1].file_id, callback.data)
        if input_file:
            await callback.message.answer_photo(photo=input_file,
                                                caption=f"🔥 БУМ! А вот и ты! Узнаешь?! - главный герой игры {slot_name} Выглядишь потрясающе!")
        else:
            await callback.message.answer("Не удалось обработать вашу аватарку, попробуйте загрузить фото в сообщении")
            return
    else:
        await callback.message.answer(
            f"🔥 Отличный выбор!\n\n"
            f"Теперь загрузите фото, чтобы примерить образ из слота {callback.data.replace('_', ' ').title()}\n\n")


@router.message(FSMClient.user_photo)
async def user_photo_handler(message: types.Message, state: FSMContext):
    await message.answer_animation(animation=loading_gif_buffered, caption="Загружаю твою аватарку...")
    data = await state.get_data()
    slot_name = data.get('slot_name')
    input_file, slot_name = await get_swapped_photo(message.photo[-1].file_id, slot_name)
    if input_file:
        kb = InlineKeyboardBuilder()
        kb.button(text='ЗАБРАТЬ ФРИСПИНЫ', callback_data='get_free_spins')
        kb.button(text='ПОПРОБОВАТЬ ЕЩЕ', callback_data='get_bonus')
        await message.answer_photo(photo=input_file,
                                   caption=f"🔥 БУМ! А вот и ты! Узнаешь?! - главный герой игры {slot_name.replace('_', ' ').title()} Выглядишь потрясающе!")
        await message.answer("🎯 И по традиции, дарим бонус для этой игры\n\n"
                             f"10 бесплатных вращений в игре {slot_name.replace('_', ' ').title()}\n\n"
                             "👇 Жми и забирай", reply_markup=kb.as_markup())
        await state.clear()
    else:
        await message.answer("Не удалось обнаружить лицо на фото, попробуйте загрузить другое изображение")


@router.callback_query(F.data == 'use_avatar')
@router.message(F.photo)
async def use_avatar_handler(callback: types.CallbackQuery | types.Message, state: FSMContext):
    await bot.send_animation(chat_id=callback.from_user.id,
                             animation=loading_gif_buffered,
                             caption=(
                                 "⚙️ <b>Загружаем твое альтер-эго...</b>\n\n"
                                 "⏳ <i>Это займет несколько секунд. В это время твоя реальность переплетается с азартом...</i>"
                             )
                             )

    no_avatar_text = (
        "❗ <b>Не удалось обработать ваше фото</b>\n\n"
        "📸 <i>Пожалуйста, отправьте фотографию с лицом, чтобы попробовать снова.</i>"
    )

    if isinstance(callback, types.CallbackQuery):
        await callback.answer()
        photos = await bot.get_user_profile_photos(user_id=callback.from_user.id)
        file_id = photos.photos[0][-1].file_id if photos.total_count else None
    else:
        photos = callback.photo
        file_id = photos[-1]

    if file_id:
        hero_name = random.choice(list(hero_faces.keys()))
        input_file, slot_name = await get_swapped_photo(file_id, hero_name)

        if input_file:
            text = await random_text(slot_name)
            btn = await create_rega_btn(callback.from_user.id, text="ИГРАТЬ!")
            await bot.send_photo(chat_id=callback.from_user.id,
                                 photo=input_file,
                                 caption=text,
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[btn]])
                                 )

            # Only send delayed registration message if it's a callback query (not a direct photo)
            if isinstance(callback, types.CallbackQuery):
                btn = await create_rega_btn(callback.from_user.id, text="ИГРАТЬ!")
                kb = InlineKeyboardMarkup(inline_keyboard=[[btn]])
                asyncio.create_task(send_delayed_message(
                    callback.from_user.id,
                    delay=20,
                    message_text="💬 <b>И кстати, пока ты здесь, спешу поделиться советом..</b>\n\n"
                                 "🎰 <b>Казино SLOTTICA, кроме фриспинов, ДАРИТ ВСЕМ НОВЫМ ИГРОКАМ +200% на первое пополнение!</b>\n\n"
                                 "⚡️ <i>Не забудь активировать бонус сразу после регистрации.</i>",
                    kb=kb
                ))

            kb = InlineKeyboardBuilder()
            btn = await create_rega_btn(callback.from_user.id, text="🎰 ЗАБРАТЬ ФРИСПИНЫ 🎰 (рега)")
            kb.add(btn)
            kb.button(text='👻 БОЛЬШЕ БОНУСОВ ТУТ 👻', callback_data='bonus')
            kb.adjust(1)
            asyncio.create_task(send_delayed_message(callback.from_user.id, delay=3,
                                                     message_text="<b>Как и обещали — дарим бонус для этого слота</b>\n\n"
                                                                  "🎁 <b>10 бесплатных вращений в игре [название слота]</b>\n\n"
                                                                  "🏆 <i>Прямо сейчас в этом слоте игрок #45701 поймал множитель х882</i>\n\n"
                                                                  "<b>Попробуй превзойти этот результат!</b> <i>А с бонусом у тебя уже есть фора!</i>\n\n"
                                                                  "👇 👇 <b>Жми и забирай</b>",
                                                     kb=kb.as_markup()))
            await asyncio.sleep(8)
            await get_bonus_handler(callback, state=state)
            return

    # Якщо не вдалося обробити фото або його немає
    await callback.message.answer(no_avatar_text)


@router.callback_query(F.data == 'get_free_spins')
async def get_free_spins_handler(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder()
    kb.button(text='БОНУС 200%  ', callback_data='get_bonus')
    await callback.message.answer("И кстати, пока ты здесь, спешу поделиться советом..\n\n"
                                  "Казино SLOTTICA, кроме фриспинов, ДАРИТ ВСЕМ НОВЫИ ИГРОКАМ +200% на первое пополнение!\n\n"
                                  "Не забудь активировать бонус сразу после регистрации"
                                  , reply_markup=kb.as_markup())


@router.callback_query(F.data == 'get_bonus')
@router.message(Command('generate'))
async def get_bonus_handler(event: Union[types.CallbackQuery, types.Message], state: FSMContext):
    kb = await generate_slots_kb()
    await state.set_state(FSMClient.slot_name)
    user_id = event.from_user.id
    await bot.send_message(user_id,
                           "👑 Хочешь примерить другие образы?\n\n"
                           "Каждое новое перевоплощение = новый бонус!\n\n"
                           "👇 Выбери слот"
                           , reply_markup=kb)
    btn = await create_rega_btn(user_id, text="БОНУС +200%")
    kb = InlineKeyboardMarkup(inline_keyboard=[[btn]])
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
