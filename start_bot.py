import asyncio
import os

import cv2
import insightface
import logging

import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from aiogram.types import BufferedInputFile, BotCommand
from insightface.app import FaceAnalysis


class FaceAnalysis2(FaceAnalysis):
    def get(self, img, max_num=0, det_size=(640, 640)):
        if det_size is not None:
            self.det_model.input_size = det_size

        return super().get(img, max_num)


def register_routers(dp):
    from handlers import main
    from handlers import bonus
    from handlers import help
    dp.include_router(bonus.router)
    dp.include_router(main.router)
    dp.include_router(help.router)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="bonus", description="ваши бонусы собраны здесь"),
        BotCommand(command="generate", description="создайте другие образы"),
        BotCommand(command="help", description="нужна помощь? - напишите"),
    ]
    await bot.set_my_commands(commands)


load_dotenv()

TOKEN_API = os.environ.get('BOT_TOKEN')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = FaceAnalysis2(name='buffalo_l')
app.prepare(ctx_id=-1)
swapper = insightface.model_zoo.get_model('inswapper_128.onnx', download=True, download_zip=True)

hero_faces = {}

for hero_file in os.listdir('static/images'):
    hero_path = os.path.join('static/images', hero_file)
    hero_image = cv2.imread(hero_path)
    faces = app.get(hero_image)

    if faces:
        hero_name = os.path.splitext(hero_file)[0]  # Remove file extension
        hero_faces[hero_name] = faces[0]
    else:
        logging.warning(f"No face detected in {hero_file}")
bot = Bot(token=TOKEN_API, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()
with open('static/loading.gif', 'rb') as gif_file:
    loading_gif_bytes = gif_file.read()
    loading_gif_buffered = BufferedInputFile(loading_gif_bytes, filename='loading.gif')


async def start():
    await set_bot_commands(bot)
    register_routers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start())
