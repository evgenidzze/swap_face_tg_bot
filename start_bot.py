import os
import cv2
import insightface
import logging
import sys

from aiogram import Bot, executor
from aiogram.types import BotCommand
from insightface.app import FaceAnalysis

from create_bot import dp, scheduler
from utils.db_manage import on_startup_db


class FaceAnalysis2(FaceAnalysis):
    def get(self, img, max_num=0, det_size=(640, 640)):
        if det_size is not None:
            self.det_model.input_size = det_size

        return super().get(img, max_num)


def register_handlers(dp):
    """Register all handlers for the dispatcher"""
    from handlers import main
    from handlers import bonus
    from handlers import help
    from handlers import main_admin

    # Register handlers from each module
    main.register_handlers(dp)
    bonus.register_bonus_handlers(dp)
    help.register_help_handlers(dp)
    main_admin.register_admin_handlers(dp)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="bonus", description="ваши бонусы собраны здесь"),
        BotCommand(command="generate", description="создайте другие образы"),
        BotCommand(command="help", description="нужна помощь? - напишите"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(dp):
    """Actions performed on startup"""
    scheduler.start()
    await set_bot_commands(dp.bot)
    await on_startup_db(dp)




logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Initialize face analysis
app = FaceAnalysis2(name='buffalo_l')
app.prepare(ctx_id=-1)
swapper = insightface.model_zoo.get_model('inswapper_128.onnx', download_zip=True)

# Dictionary to store hero faces
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


if __name__ == "__main__":
    register_handlers(dp)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)