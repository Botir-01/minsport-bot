import logging

from aiogram.utils.executor import start_webhook
from aiogram.utils.executor import Executor
from handlers import client, other
from create_bot import dp, bot

from create_bot import WEBHOOK_HOST, WEBHOOK_PATH, WEBAPP_PORT, WEBAPP_HOST, WEBHOOK_URL


logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    print("Bot is online")
    await bot.set_webhook(WEBHOOK_URL)


client.register_handlers_client(dp)

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )



