import requests
from aiogram import Router, F
from aiogram.types import Message
from app.keyboards import main_menu_keyboard

order_router = Router()
BASE_URL = "http://127.0.0.1:8000/api/"


@order_router.message(F.text == 'В главное меню')
async def back(message: Message):
    await message.answer('Вы успешно вернулись в главное меню!', reply_markup=main_menu_keyboard)


@order_router.message(F.text == 'Самовывоз')
async def pickup(message: Message):
    await message.answer('Вы можете выбрать любой склад из списка. Для уточнения оставшегося места обратитесь \
в службу поддержки')
    response = requests.get(f'{BASE_URL}storage')
    response.raise_for_status()
    storages = response.json()
    list_of_storages = ''
    for number, storage in enumerate(storages, start=1):
        list_of_storages += f'''{number}. {storage['name']}.
        Адрес склада - {storage['location']}.
        Максимальная вместимость - {storage['max_capacity']}.\n\n'''
    await message.answer(text=list_of_storages)


@order_router.message(F.text == 'Курьер')
async def courier(message: Message):
    await message.answer('')
