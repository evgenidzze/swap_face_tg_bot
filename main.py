import asyncio
import os

import cv2
import insightface
from aiogram.filters import Command
from dotenv import load_dotenv
from insightface.app import FaceAnalysis
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BufferedInputFile
import numpy as np
from io import BytesIO
load_dotenv()

TOKEN_API = os.environ.get('BOT_TOKEN')

bot = Bot(token=TOKEN_API)
dp = Dispatcher()

# Ініціалізуємо моделі заздалегідь, щоби не кожного разу
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=-1, det_size=(640, 640))
swapper = insightface.model_zoo.get_model('inswapper_128.onnx', download=True, download_zip=True)

# Статичне обличчя, яке підставлятимемо
pearl_image = cv2.imread('pearl.jpg')
man_face = app.get(pearl_image)[0]


@dp.message(Command('start'))
async def start_handler(message: types.Message):
    await message.reply("Надішли фото, і я підставлю туди інше обличчя 😉")


@dp.message(F.photo)
async def photo_handler(message: types.Message):
    photo = message.photo[-1]  # найвища якість
    photo_bytes = BytesIO()
    await bot.download(file=photo.file_id, destination=photo_bytes)
    photo_bytes.seek(0)

    # Конвертуємо у формат OpenCV
    np_arr = np.frombuffer(photo_bytes.read(), np.uint8)
    user_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Отримуємо обличчя
    faces = app.get(user_img)
    if not faces:
        await message.reply("Не знайшов обличчя 😢. Спробуй інше фото.")
        return

    user_face = faces[0]

    # Підставляємо
    swapped = swapper.get(pearl_image.copy(), man_face, user_face, paste_back=True)

    # Кодуємо для відправки
    _, buffer = cv2.imencode('.jpg', swapped)
    image_io = BytesIO(buffer.tobytes())
    image_io.seek(0)
    input_file = BufferedInputFile(file=image_io.getvalue(), filename="swapped.jpg")
    await message.answer_photo(photo=input_file, caption="Готово! 🔁")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
