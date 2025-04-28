import cv2
import numpy as np
from aiogram.types import BufferedInputFile
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


async def get_swapped_photo(photos, hero_name):
    photo = photos[-1]
    photo_bytes = BytesIO()
    await bot.download(file=photo.file_id, destination=photo_bytes)
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

