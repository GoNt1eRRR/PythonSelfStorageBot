from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать ячейку')],
    [KeyboardButton(text='Заказы')],
    [KeyboardButton(text='Тарифы'),
     KeyboardButton(text='Правила хранения')],
], resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню',
)

consent_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Я подтверждаю пользовательское соглашение")]
    ],
    resize_keyboard=True
)

order_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Курьер')],
    [KeyboardButton(text='Самовывоз')],
    [KeyboardButton(text='В главное меню')],
], resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню',
)


async def inline_my_orders(my_orders):
    keyboard = InlineKeyboardBuilder()
    for order in my_orders:
        keyboard.add(InlineKeyboardButton(text=f'от {order['start_date']}', url='google.com'))
    return keyboard.adjust(1).as_markup()
