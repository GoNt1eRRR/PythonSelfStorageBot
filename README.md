# PythonSelfStorageBot

Telegram-бот для управления хранением вещей на складах. Бот позволяет пользователям бронировать ячейки для хранения, выбирать способ доставки (курьером или самовывозом), получать информацию о тарифах и правилах хранения.

## Функционал

- **Регистрация пользователей**: Бот автоматически регистрирует новых пользователей, запрашивая имя.
- **Бронирование ячейки**:
  - Выбор удобного способа доставки: курьер или самовывоз.
  - Заполнение необходимых данных (ФИО, телефон, адрес).
- **Тарифы и правила хранения**: Возможность ознакомиться с актуальными тарифами и запрещёнными к хранению предметами.
- **Удобства**: Поддержка генерации QR-кодов для заказов.
- **Служба поддержки**: Доступ к контактной информации менеджеров для помощи и уточнений.

---

## Требования

Для запуска бота необходимы:

- Python 3.7+
- Установленные зависимости из `requirements.txt`

---

## Установка

1. Склонируйте репозиторий:

```bash
git clone https://github.com/YourRepo/PythonSelfStorageBot.git
```

2. Создайте виртуальное окружение:

```bash
python3 -m venv env
source env/bin/activate  # Для Windows: env\Scripts\activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Получите токен для бота через [BotFather](https://telegram.me/BotFather).

5. Создайте файл `.env` в корне проекта и добавьте туда токен:

```text
TG_TOKEN=ваш_токен
```

6. Запустите бота:

```bash
python run.py
```

---

## Структура проекта

- `run.py` — главный файл для запуска бота.
- `keyboards.py` — обработка клавиатур для взаимодействия с пользователями.
- `order_handlers.py` — логика работы с заказами и курьерской доставкой.
- `start_handler.py` — обработка команды `start` и регистрация пользователей.
- `secondary_handlers.py` — команды `help`, `support`, а также обработка тарифов и правил хранения.

---

## Основной функционал

### Регистрация

При первом запуске бота пользователю предлагается зарегистрироваться, указав имя. После этого ему необходимо подтвердить пользовательское соглашение.

### Бронирование ячейки

1. Нажмите "Заказать ячейку".
2. Выберите способ доставки:
   - **Курьер**: Укажите склад, адрес, ФИО и телефон.
   - **Самовывоз**: Выберите удобный склад из списка.
3. Подтвердите данные.

### Управление заказами

- Просмотр активных заказов и их статусов.
- Генерация QR-кода для завершения заказа.

### Информация

- **Тарифы**: Информация о стоимости хранения.
- **Правила хранения**: Список запрещённых к хранению предметов.

### Связь с менеджером

Для связи с менеджером можно использовать кнопку "support", которая позволяет пользователю связаться удобным способом с ним и получить помощь.

### Структура обработки запросов

- **Выбор склада**: Пользователь выбирает склад, который ему удобен. Бот отображает список доступных складов с адресами и вместимостью через API.

- **Выбор способа доставки**: При выборе курьерской доставки бот запрашивает данные о клиенте и адрес, а при самовывозе отображает информацию о складе.

- **Подтверждение и оформление заказа**: Пользователь вводит свои данные (ФИО, телефон, адрес). После подтверждения бот создаёт заказ и сообщает детали.

- **Генерация QR-кодов**: Бот создаёт уникальный QR-код для подтверждения заказа, который можно использовать для доступа к складу.

---

## Пример кода генерации QR-кода

```python
async def issue_qr_code(callback: CallbackQuery):
    qr_data = f"SelfStorage Order #{order_id}"
    qr_img = qrcode.make(qr_data)

    bio = BytesIO()
    qr_img.save(bio, format='PNG')
    bio.seek(0)

    await callback.message.answer_document(
        document=BufferedInputFile(bio.read(), filename="order_qr.png"),
        caption=f"QR-код для заказа №{order_id}"
    )
```
