import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from dotenv import load_dotenv
load_dotenv()

TOKEN_API = os.environ.get('BOT_TOKEN')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')


job_stores = {
    "default": RedisJobStore(db=0,
                             jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
                             host="redis",  # Updated to use service name
                             port=6379, password=REDIS_PASSWORD
                             )
}

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))
storage = MemoryStorage()

bot = Bot(token=TOKEN_API, parse_mode='html')
dp = Dispatcher(bot, storage=storage)
