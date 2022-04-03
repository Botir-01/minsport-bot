import logging

from aiogram import executor
from handlers import client
from create_bot import dp

logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    print("Bot is online")

client.register_handlers_client(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)