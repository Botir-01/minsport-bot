from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from decouple import config


API_TOKEN = config('API_TOKEN')
WEBHOOK_HOST = config('WEBHOOK_HOST')
WEBHOOK_PATH = config('WEBHOOK_PATH')
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
storage = MemoryStorage()

WEBAPP_HOST = config('WEBAPP_HOST')
WEBAPP_PORT = config('WEBAPP_PORT')


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())