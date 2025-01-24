from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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