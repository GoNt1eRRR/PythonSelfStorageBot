import requests
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards import main_menu_keyboard, order_keyboard

order_router = Router()
BASE_URL = "http://127.0.0.1:8000/api/"


class CourierOrder(StatesGroup):
    waiting_for_storage_choice = State()
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_user_address = State()


@order_router.message(F.text == 'Курьер')
async def courier_order_start(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{BASE_URL}storage")
        response.raise_for_status()
        storages = response.json()

        if not storages:
            await message.answer("К сожалению, сейчас нет доступных складов.")
            return

        buttons = []
        for storage in storages:
            callback_data = f"choose_storage:{storage['name']}"
            button_text = f"{storage['name']} ({storage['location']})"
            buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(
            "Пожалуйста, выберите склад, который вам удобен:",
            reply_markup=keyboard
        )
        await state.set_state(CourierOrder.waiting_for_storage_choice)

    except requests.RequestException:
        await message.answer(
            "Произошла ошибка при загрузке складов. Попробуйте позднее или обратитесь в поддержку /help"
        )


@order_router.callback_query(lambda c: c.data and c.data.startswith("choose_storage"))
async def courier_order_storage_chosen(callback: CallbackQuery, state: FSMContext):
    _, storage_name = callback.data.split("choose_storage:")

    await state.update_data(chosen_storage=storage_name.strip())

    await callback.message.answer(
        "Отлично! Теперь введите, пожалуйста, ваше ФИО:"
    )
    await state.set_state(CourierOrder.waiting_for_full_name)
    await callback.answer()


@order_router.message(CourierOrder.waiting_for_full_name)
async def courier_order_get_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)

    await message.answer("Введите, пожалуйста, ваш номер телефона:")
    await state.set_state(CourierOrder.waiting_for_phone)


@order_router.message(CourierOrder.waiting_for_phone)
async def courier_order_get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone_number=phone)

    await message.answer("Введите адрес, по которому нужно приехать курьеру:")
    await state.set_state(CourierOrder.waiting_for_user_address)


@order_router.message(CourierOrder.waiting_for_user_address)
async def courier_order_get_user_address(message: Message, state: FSMContext):
    user_address = message.text.strip()
    await state.update_data(user_address=user_address)

    data = await state.get_data()
    telegram_id = message.from_user.id

    payload = {
        "customer": str(telegram_id),
        "storage": data["chosen_storage"],
        "address": data["user_address"],
        "phone_number": data["phone_number"],
        "full_name": data["full_name"],
    }

    try:
        response = requests.post(f"{BASE_URL}order/", json=payload)
        if response.status_code == 201:
            await message.answer(
                "Заказ успешно оформлен! Курьер свяжется с вами в ближайшее время.\n"
                "Если возникнут вопросы, нажмите /help и обратитесь в поддержку.",
                reply_markup=main_menu_keyboard
            )
        else:
            await message.answer(
                "Не удалось оформить заказ. Попробуйте ещё раз или свяжитесь с поддержкой /help"
            )
    except requests.RequestException:
        await message.answer(
            "Произошла ошибка при оформлении заказа. Попробуйте ещё раз или свяжитесь с поддержкой /help"
        )

    await state.clear()


@order_router.message(F.text == 'В главное меню')
async def back(message: Message):
    await message.answer('Вы успешно вернулись в главное меню!', reply_markup=main_menu_keyboard)


@order_router.message(F.text == 'Заказать ячейку')
async def order(message: Message):
    await message.answer(
        '''Как бы вам было удобнее отправить груз? 
                Мы предлагаем бесплатную доставку ваших вещей до выбранного склада! 
                Наш курьер приедет к вам, аккуратно измерит размеры груза и подберёт идеальный тариф. 
                Выбирайте удобный способ доставки ниже!''',
        reply_markup=order_keyboard
    )


@order_router.message(F.text == 'Самовывоз')
async def pickup(message: Message):
    await message.answer('Вы можете выбрать любой склад из списка. Для уточнения оставшегося места обратитесь \
в службу поддержки /help')
    response = requests.get(f'{BASE_URL}storage')
    response.raise_for_status()
    storages = response.json()
    list_of_storages = ''
    for number, storage in enumerate(storages, start=1):
        list_of_storages += f'''{number}. {storage['name']}.
        Адрес склада - {storage['location']}.
        Максимальное кол-во ячеек - {storage['max_capacity']}.\n\n'''
    await message.answer(text=list_of_storages)


@order_router.message(F.text == 'Курьер')
async def courier(message: Message):
    await message.answer('')
