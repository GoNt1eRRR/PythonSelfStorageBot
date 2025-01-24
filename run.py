import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from app.handlers import router


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv("TG_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
