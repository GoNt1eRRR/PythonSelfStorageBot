import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv("TG_TOKEN"))
    dp = Dispatcher()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
