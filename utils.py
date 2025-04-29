from random import random, choice

import cv2
import numpy as np
from aiogram.types import BufferedInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from insightface.app import FaceAnalysis

from io import BytesIO

from start_bot import swapper, app, bot, hero_faces


def analyze_faces(face_analysis: FaceAnalysis, img_data: np.ndarray, det_size=(640, 640)):
    detection_sizes = [None] + [(size, size) for size in range(640, 256, -64)] + [(256, 256)]

    for size in detection_sizes:
        print(size)
        faces = face_analysis.get(img_data, det_size=size)
        if len(faces) > 0:
            return faces

    return []


async def get_swapped_photo(file_id, hero_name):
    photo_bytes = BytesIO()
    await bot.download(file=file_id, destination=photo_bytes)
    photo_bytes.seek(0)

    np_arr = np.frombuffer(photo_bytes.read(), np.uint8)
    user_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    faces = analyze_faces(app, user_img)

    if not faces:
        return False, None

    user_face = faces[0]

    # Randomly select a hero
    hero_path = f'static/images/{hero_name}.jpg'
    hero_image = cv2.imread(hero_path)
    hero_face = hero_faces[hero_name]

    # Swap faces
    swapped = swapper.get(hero_image.copy(), hero_face, user_face, paste_back=True)

    _, buffer = cv2.imencode('.jpg', swapped)
    image_io = BytesIO(buffer.tobytes())
    image_io.seek(0)
    input_file = BufferedInputFile(file=image_io.getvalue(), filename="swapped.jpg")
    hero_name = hero_name.replace('_', ' ').title()
    return input_file, hero_name


async def generate_slots_kb():
    kb = InlineKeyboardBuilder()
    for hero_name in hero_faces.keys():
        kb.button(text=hero_name.replace('_', ' ').title(), callback_data=f"{hero_name}")
    kb.adjust(1)
    return kb.as_markup()


async def random_text(slot_name):
    formatted_slot_name = slot_name.replace('_', ' ').title()
    texts = [
        f"😎 <b>Ну слушай, ты реально круто смотришься в этом образе!</b>\n<i>А хочешь за него и поиграть?</i>\n<b>Заходи в {formatted_slot_name} — кайфанём вместе!</b>",

        f"🎭 <b>Вот это превращение!</b>\n<i>Если тебе, как и нам, по кайфу — жми и загляни в {formatted_slot_name}</i>",

        f"⚡ <b>Кажется, твой герой уже готов к игре.</b>\n<i>Не тормози — заходи в {formatted_slot_name} и сорви куш!</i>",

        f"🎲 <b>Мы бы и сами зашли в игру с таким лицом!</b>\n<i>Тебе осталось только нажать — {formatted_slot_name} и войти в игру</i>",

        f"⭐ <b>Ну ты и красавчик. Герой как с афиши.</b>\n<i>Осталось только сыграть за него в {formatted_slot_name}</i>",

        f"🎯 <b>Кажется, кто-то нашёл своего идеального персонажа.</b>\n<i>Так может, и в игру за него? {formatted_slot_name} тебя уже ждёт!</i>",

        f"🔥 БУМ! А вот и ты! Узнаешь?! - главный герой игры {formatted_slot_name} Выглядишь потрясающе!",

        f"🎯 И по традиции, дарим бонус для этой игры\n\n10 бесплатных вращений в игре {formatted_slot_name}\n\nЖми и забирай"
    ]
    return choice(texts)


async def get_rega(user_id):
    return f"https://slottica-bonus.com/registration/c=02414WCeSw_RP0e0a462d27365a40f&utm_source=rafautodep&utm_campaign=0&utm_content={user_id}&utm_term=AZ"


async def create_rega_btn(user_id, text):
    rega = await get_rega(user_id)
    return InlineKeyboardButton(text=text, url=rega)