import requests
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import qrcode
from io import BytesIO
from aiogram.types import BufferedInputFile
from datetime import datetime

from app.keyboards import main_menu_keyboard, order_keyboard

order_router = Router()

BASE_URL = "https://rertgertgertg.pythonanywhere.com/api/"


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
            "Произошла ошибка при загрузке складов. Попробуйте позднее или обратитесь в поддержку /support"
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
                "Если возникнут вопросы, нажмите /help и обратитесь в поддержку /support",
                reply_markup=main_menu_keyboard
            )
        else:
            await message.answer(
                "Не удалось оформить заказ. Попробуйте ещё раз или свяжитесь с поддержкой /support"
            )
    except requests.RequestException:
        await message.answer(
            "Произошла ошибка при оформлении заказа. Попробуйте ещё раз или свяжитесь с поддержкой /support"
        )

    await state.clear()


@order_router.message(F.text == 'В главное меню')
async def back(message: Message):
    await message.answer('Вы успешно вернулись в главное меню!', reply_markup=main_menu_keyboard)


@order_router.message(F.text == 'Заказать ячейку')
async def order(message: Message):
    await message.answer(
        (
            "📦 <b>Как бы вам было удобнее отправить груз?</b>\n\n"
            "Мы предлагаем бесплатную доставку ваших вещей до выбранного склада! 🚛\n"
            "Наш курьер приедет к вам, аккуратно измерит размеры груза и подберёт идеальный тариф.\n\n"
            "⬇️ Выберите удобный способ доставки ниже!"
        ),
        parse_mode='HTML',
        reply_markup=order_keyboard
    )


@order_router.message(F.text == 'Самовывоз')
async def pickup(message: Message):
    await message.answer('Вы можете выбрать любой склад из списка. Для уточнения оставшегося места обратитесь \
в службу поддержки /support')
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


@order_router.message(F.text == 'Заказы')
async def my_orders(message: Message):
    telegram_id = message.from_user.id

    try:
        orders_response = requests.get(f"{BASE_URL}order/")
        orders_response.raise_for_status()
    except requests.RequestException:
        await message.answer("Произошла ошибка при получении заказов. Попробуйте позже.")
        return

    orders = orders_response.json()

    try:
        storage_response = requests.get(f"{BASE_URL}storage/")
        storage_response.raise_for_status()
    except requests.RequestException:
        await message.answer("Произошла ошибка при получении списка складов. Попробуйте позже.")
        return

    storages = storage_response.json()
    storage_map = {
        s["name"]: s["location"] for s in storages
    }

    user_orders = [
        order for order in orders
        if order["customer"] == str(telegram_id) and order["qr_issued"] is False
    ]

    if not user_orders:
        await message.answer("У вас нет заказов, доступных для выдачи QR-кода.")
        return

    for order in user_orders:
        order_id = order['id']
        storage_name = order['storage']
        user_address = order['address']
        phone_number = order['phone_number']
        full_name = order['full_name']
        status = order['status']
        end_date = order.get('end_date')

        if end_date:
            end_date_formatted = datetime.fromisoformat(end_date).strftime("%d.%m.%Y %H:%M")
        else:
            end_date_formatted = "Даты не установлено"

        storage_address = storage_map.get(storage_name, "Адрес склада не найден")

        text = (
            f"<b>Заказ №{order_id}</b>\n"
            f"Склад: {storage_name}\n"
            f"Адрес склада: {storage_address}\n\n"
            f"Адрес пользователя: {user_address}\n"
            f"Телефон: {phone_number}\n"
            f"ФИО: {full_name}\n"
            f"Статус: {status}\n"
            f"Дата окончания: {end_date_formatted}\n"
        )

        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Выдать QR?",
                        callback_data=f"issue_qr:{order_id}"
                    )
                ]
            ]
        )

        await message.answer(text, parse_mode="HTML", reply_markup=inline_kb)


@order_router.callback_query(F.data.startswith("issue_qr"))
async def confirm_issue_qr(callback: CallbackQuery):
    _, order_id = callback.data.split(":")
    order_id = order_id.strip()

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"confirm_qr:{order_id}"),
                InlineKeyboardButton(text="Нет", callback_data="cancel_qr")
            ]
        ]
    )

    await callback.message.answer(
        f"Подтвердите выдачу QR-кода для заказа №{order_id}:",
        reply_markup=confirm_keyboard
    )
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


@order_router.callback_query(F.data.startswith("confirm_qr"))
async def issue_qr_code(callback: CallbackQuery):
    _, order_id = callback.data.split(":")
    order_id = order_id.strip()

    qr_data = f"SelfStorage Order #{order_id}"
    qr_img = qrcode.make(qr_data)

    bio = BytesIO()
    qr_img.save(bio, format='PNG')

    bio.seek(0)
    qr_bytes = bio.read()

    doc = BufferedInputFile(qr_bytes, filename="order_qr.png")

    patch_url = f"{BASE_URL}order/{order_id}/"
    files = {
        "qr_code": ("qr.png", BytesIO(qr_bytes), "image/png")
    }
    data = {"qr_issued": True}

    try:
        response = requests.patch(patch_url, data=data, files=files)
        if response.status_code not in (200, 202):
            await callback.message.answer(
                f"Не удалось обновить заказ №{order_id}. "
                f"Сервер вернул код {response.status_code}: {response.text}"
            )
            await callback.answer()
            return
    except requests.RequestException:
        await callback.message.answer("Произошла ошибка при обновлении заказа. Попробуйте ещё раз.")
        await callback.answer()
        return

    bio.seek(0)
    await callback.message.answer_document(
        document=doc,
        caption=f"QR-код для заказа №{order_id}"
    )

    await callback.message.answer(
        "QR-код успешно выдан и сохранён в базе! Если возникнут вопросы, нажмите /support"
    )
    await callback.answer()


@order_router.callback_query(F.data == "cancel_qr")
async def cancel_issue_qr(callback: CallbackQuery):
    await callback.message.answer("Выдача QR-кода отменена.")
    await callback.answer()
