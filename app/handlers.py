import requests
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from app.keyboards import consent_keyboard, main_menu_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

BASE_URL = "http://127.0.0.1:8000/api/"


class RegistrationStates(StatesGroup):
    waiting_for_name = State()


@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    response = requests.get(f'{BASE_URL}custom-user/', params={"telegram_id": telegram_id})

    if response.status_code == 200:
        users = response.json()
        user = next((u for u in users if u["telegram_id"] == str(telegram_id)), None)
        if user:
            await message.answer(
                "🎉 Добро пожаловать в бота! 🎉\n\n"
                "Вы снова с нами, и это значит, что ваши вещи всегда в безопасности.\n\n"
                "📦 Чего вы хотите сегодня? Выбрать ячейку? Посмотреть тарифы? Всё готово для вашего удобства! 🚀",
                reply_markup=main_menu_keyboard
            )
            return

    await message.answer("Кажется, вас нет в нашей базе. Укажите, пожалуйста, своё имя:")
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(RegistrationStates.waiting_for_name)
async def process_user_name(message: Message, state: FSMContext):
    user_name = message.text
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username

    response = requests.post(
        f"{BASE_URL}custom-user/",
        json={
            "username": user_name,
            "telegram_id": telegram_id,
            "telegram_name": telegram_name
        }
    )

    if response.status_code == 201:
        await message.answer(
            "Спасибо! Вы успешно зарегистрированы.\n"
            "Теперь подтвердите пользовательское соглашение:",
            reply_markup=consent_keyboard
        )

        consent_file = FSInputFile("app/Agreement.pdf")
        await message.answer_document(document=consent_file)
    else:
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")

    await state.clear()


@router.message(F.text == "Я подтверждаю пользовательское соглашение")
async def user_consented(message: Message):
    await message.answer(
        "✨ Спасибо за доверие! 🎉\n\n"
        "Теперь вы можете воспользоваться нашим удобным сервисом:\n"
        "📦 Забронировать ячейку для хранения вещей\n"
        "🔍 Просмотреть тарифы и условия хранения\n"
        "🧹 Держать ваши вещи в порядке и сохранности.\n\n"
        "Выберите нужный раздел и начнём работать! 🚀",
        reply_markup=main_menu_keyboard
    )