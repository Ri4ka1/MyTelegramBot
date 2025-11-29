import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update, Message
from aiogram.filters import CommandStart
from aiogram import F # Фильтр для обработки нажатий кнопок
from aiohttp import web 

# =================================================================
# 1. КОНФИГУРАЦИЯ БОТА И WEBHOOK (Оставляем как было для Render)
# =================================================================

# Получаем токен из переменной окружения (как настроено на Render)
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    # Используй этот RAISE, если забыл добавить BOT_TOKEN в Render Environment Variables
    raise ValueError("Переменная окружения 'BOT_TOKEN' не найдена.")

# Параметры Webhook. Используют переменные окружения Render
WEBHOOK_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME') 
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'https://{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки веб-сервера
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 8080))

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =================================================================
# 2. ФУНКЦИИ ГЕНЕРАЦИИ КЛАВИАТУР (КНОПКИ)
# =================================================================

# --- 2.1. Главное меню ---
def get_main_keyboard() -> InlineKeyboardMarkup:
    """Генерирует главное меню: Машины, Недвижимость, Скины/Аксессуары."""
    buttons = [
        [
            InlineKeyboardButton(text="🚗 Машины", callback_data="category_cars"),
            InlineKeyboardButton(text="🏠 Недвижимость", callback_data="category_property")
        ],
        [
            InlineKeyboardButton(text="👕 Скины/Аксессуары", callback_data="category_skins")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- 2.2. Меню "Машины" ---
def get_cars_keyboard() -> InlineKeyboardMarkup:
    """Генерирует меню выбора класса машин."""
    buttons = [
        [
            InlineKeyboardButton(text="Низкий Класс", callback_data="car_low"),
            InlineKeyboardButton(text="Средний Класс", callback_data="car_medium")
        ],
        [
            InlineKeyboardButton(text="Высокий Класс", callback_data="car_high"),
            InlineKeyboardButton(text="Грузовой Класс", callback_data="car_truck")
        ],
        [
            InlineKeyboardButton(text="Мотоциклы", callback_data="car_moto"),
            InlineKeyboardButton(text="Эксклюзивные Авто", callback_data="car_exclusive")
        ],
        [
            InlineKeyboardButton(text="⬅️ В Главное Меню", callback_data="go_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- 2.3. Меню "Недвижимость" ---
def get_property_keyboard() -> InlineKeyboardMarkup:
    """Генерирует меню выбора недвижимости."""
    buttons = [
        [
            InlineKeyboardButton(text="Квартиры", callback_data="prop_apartment"),
            InlineKeyboardButton(text="Дома", callback_data="prop_house")
        ],
        [
            InlineKeyboardButton(text="Гаражи", callback_data="prop_garage")
        ],
        [
            InlineKeyboardButton(text="⬅️ В Главное Меню", callback_data="go_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- 2.4. Меню "Скины/Аксессуары" ---
def get_skins_keyboard() -> InlineKeyboardMarkup:
    """Генерирует меню выбора скинов и аксессуаров."""
    buttons = [
        [
            InlineKeyboardButton(text="Скины", callback_data="skin_skins"),
            InlineKeyboardButton(text="Аксессуары", callback_data="skin_accessories")
        ],
        [
            InlineKeyboardButton(text="⬅️ В Главное Меню", callback_data="go_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =================================================================
# 3. ОБРАБОТЧИКИ КОМАНД И ТЕКСТА
# =================================================================

@dp.message(CommandStart())
async def handle_start(message: Message):
    """Отвечает на команду /start и показывает главное меню."""
    await message.answer(
        "**Здравствуйте!** Вы попали в бот для купли/продажи на **40 сервере** игры BLACK RUSSIA!",
        reply_markup=get_main_keyboard()
    )

@dp.message()
async def handle_text(message: Message):
    """Игнорирует любой текст, кроме /start."""
    await message.answer("Пожалуйста, используйте кнопки меню или команду /start.")


# =================================================================
# 4. ОБРАБОТЧИКИ НАЖАТИЙ НА КНОПКИ (CALLBACK QUERIES)
# =================================================================

# --- 4.1. Обработка Главного Меню ---

@dp.callback_query(F.data == "category_cars")
async def handle_category_cars(callback: types.CallbackQuery):
    """Переход в меню машин."""
    await callback.message.edit_text(
        "**Выберите тип транспорта:**",
        reply_markup=get_cars_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "category_property")
async def handle_category_property(callback: types.CallbackQuery):
    """Переход в меню недвижимости."""
    await callback.message.edit_text(
        "**Выберите тип недвижимости:**",
        reply_markup=get_property_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "category_skins")
async def handle_category_skins(callback: types.CallbackQuery):
    """Переход в меню скинов/аксессуаров."""
    await callback.message.edit_text(
        "**Выберите:**",
        reply_markup=get_skins_keyboard()
    )
    await callback.answer()

# --- 4.2. Обработка Кнопок Второго Уровня (для Машин) ---

@dp.callback_query(F.data.startswith("car_"))
async def handle_car_selection(callback: types.CallbackQuery):
    """Обработка выбора класса машины и возврат в главное меню."""
    # callback.data будет, например, 'car_low'
    
    # Редактируем сообщение, чтобы показать результат и вернуть ГЛАВНОЕ МЕНЮ
    await callback.message.edit_text(
        f"Вы выбрали класс транспорта. **(Пока что здесь нет контента)**.\n\n"
        f"Возвращаемся в главное меню:",
        reply_markup=get_main_keyboard()
    )
    # Показываем уведомление внизу экрана
    await callback.answer(text="Выбор класса сохранен!")

# --- 4.3. Обработка Кнопок Второго Уровня (для Недвижимости) ---

@dp.callback_query(F.data.startswith("prop_"))
async def handle_prop_selection(callback: types.CallbackQuery):
    """Обработка выбора недвижимости и возврат в главное меню."""
    await callback.message.edit_text(
        f"Вы выбрали тип недвижимости. **(Пока что здесь нет контента)**.\n\n"
        f"Возвращаемся в главное меню:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer(text="Выбор недвижимости сохранен!")

# --- 4.4. Обработка Кнопок Второго Уровня (для Скинов) ---

@dp.callback_query(F.data.startswith("skin_"))
async def handle_skin_selection(callback: types.CallbackQuery):
    """Обработка выбора скинов/аксессуаров и возврат в главное меню."""
    await callback.message.edit_text(
        f"Вы выбрали категорию скинов/аксессуаров. **(Пока что здесь нет контента)**.\n\n"
        f"Возвращаемся в главное меню:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer(text="Выбор категории сохранен!")

# --- 4.5. Возврат в Главное Меню из любого места ---

@dp.callback_query(F.data == "go_main")
async def handle_go_main(callback: types.CallbackQuery):
    """Возвращает пользователя в главное меню."""
    await callback.message.edit_text(
        "**Здравствуйте!** Вы попали в бот для купли/продажи на **40 сервере** игры BLACK RUSSIA!",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


# =================================================================
# 5. ФУНКЦИИ УПРАВЛЕНИЯ WEBHOOK (Не трогать, это для Render)
# =================================================================

async def on_startup(app):
    logging.info(f"Устанавливаю Webhook на URL: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)
    
async def on_shutdown(app):
    logging.info("Удаляю Webhook...")
    await bot.delete_webhook()
    await bot.session.close()

async def webhook_handler(request):
    if request.match_info.get('token') == TOKEN:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={'bot': bot})
        await dp.feed_update(bot, update)
        return web.Response()
    else:
        return web.Response(status=403)
        
if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    
    logging.info(f"Запуск веб-сервера на {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
