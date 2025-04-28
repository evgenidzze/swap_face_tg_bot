import random

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import use_avatar_kb
from start_bot import bot, loading_gif_buffered, hero_faces
from utils import get_swapped_photo, generate_slots_kb

from aiogram import types, F, Router

router = Router()

class FSMClient(StatesGroup):
    user_photo = State()
    slot_name = State()


@router.message(Command('start'))
async def start_handler(message: types.Message):
    await message.reply(
        "🎭 CasinoFace - бот, который превращает тебя в героя культовых азартных игр!\n\n"
        "👀 Хочешь узнать, кем бы ты был в мире ставок и больших выигрышей?\n\n"
        "🎁 Загрузи фото - и получи свой образ и БОНУС на игру, в которую ты идеально впишешься!\n\n"
        "⬇️ Просто отправь фото, либо разреши боту использовать твою аватарку - и узнай, на какого героя слота ты похож больше всего)\n\n"
        "Убедись, что на фото хорошо видно лицо, иначе бот не сможет создать изображение"
        , reply_markup=use_avatar_kb.as_markup())


@router.callback_query(F.data == 'use_avatar')
async def use_avatar_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer_animation(animation=loading_gif_buffered, caption="Загружаю твою аватарку...")
    photos = await bot.get_user_profile_photos(user_id=callback.from_user.id)
    if photos.total_count:
        hero_name = random.choice(list(hero_faces.keys()))

        input_file, slot_name = await get_swapped_photo(photos.photos[0], hero_name)
        if input_file:
            await callback.message.answer_photo(photo=input_file,
                                                caption=f"🔥 БУМ! А вот и ты! Узнаешь?! - главный герой игры {slot_name} Выглядишь потрясающе!")
        else:
            await callback.message.answer("Не удалось обработать вашу аватарку, попробуйте загрузить фото в сообщении")
            return
    else:
        await callback.message.answer("У вас нет аватарки, загрузите фото в сообщении")
        return


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
async def get_bonus_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    kb = await generate_slots_kb()
    await state.set_state(FSMClient.slot_name)
    await callback.message.answer(
        "👑 Хочешь примерить другие образы?\n\n"
        "Каждое новое перевоплощение = новый бонус!\n\n"
        "👇 Выбери слот"
        , reply_markup=kb)


@router.callback_query(FSMClient.slot_name)
async def slot_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(slot_name=callback.data)
    await state.set_state(FSMClient.user_photo)
    photos = await bot.get_user_profile_photos(user_id=callback.from_user.id)
    if photos.total_count:
        input_file, slot_name = await get_swapped_photo(photos.photos[0], callback.data)
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
    input_file, slot_name = await get_swapped_photo(message.photo, slot_name)
    if input_file:
        kb = InlineKeyboardBuilder()
        kb.button(text='ЗАБРАТЬ ФРИСПИНЫ', callback_data='get_free_spins')
        kb.button(text='ПОПРОБОВАТЬ ЕЩЕ', callback_data='get_bonus')
        await message.answer_photo(photo=input_file,
                                   caption=f"🔥 БУМ! А вот и ты! Узнаешь?! - главный герой игры {slot_name.replace('_', ' ').title()} Выглядишь потрясающе!")
        await message.answer("🎯 И по традиции, дарим бонус для этой игры\n\n"
                             f"10 бесплатных вращений в игре {slot_name.replace('_', ' ').title()}\n\n"
                             "👇 Жми и забирай")
        await state.clear()
    else:
        await message.answer("Не удалось обнаружить лицо на фото, попробуйте загрузить другое изображение")


@router.message(F.photo)
async def photo_handler(message: types.Message):
    hero_name = random.choice(list(hero_faces.keys()))

    input_file, slot_name = await get_swapped_photo(message.photo, hero_name)
    if input_file:
        kb = InlineKeyboardBuilder()
        kb.button(text='ЗАБРАТЬ ФРИСПИНЫ', callback_data='get_free_spins')
        await message.answer_photo(photo=input_file,
                                   caption=f"🔥 БУМ! А вот и ты! Узнаешь?! - главный герой игры {slot_name} Выглядишь потрясающе!\n\n"
                                           f"🎯 Как и обещали - дарим бонус для этого слота\n\n"
                                           f"10 бесплатных вращений в игре [название слота]\n\n"
                                           f"Прямо сейчас в этом слоте игрок #45701 поймал множитель х882\n\n"
                                           f"🔥 Попробуй превзойти этот результат! А с бонусом у тебя уже есть фора!\n\n"
                                           f"👇 Жми и забирай", reply_markup=kb.as_markup())
    else:
        await message.answer("Не удалось обнаружить лицо на фото, попробуйте загрузить другое изображение")


