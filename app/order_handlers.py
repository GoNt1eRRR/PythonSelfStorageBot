from aiogram import Router, F
from aiogram.types import Message
from app.keyboards import main_menu_keyboard

order_router = Router()


@order_router.message(F.text == 'Назад')
async def back(message: Message):
    await message.answer('Вы успешно вернулись в главное меню!',reply_markup=main_menu_keyboard)


@order_router.message(F.text == 'Самовывоз')
async def pickup(message: Message):
    await message.answer('')


@order_router.message(F.text == 'Курьер')
async def courier(message: Message):
    await message.answer('')
