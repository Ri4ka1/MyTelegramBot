import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message
from aiogram.filters import CommandStart
from aiohttp import web

# =================================================================
# 1. КОНФИГУРАЦИЯ БОТА И WEBHOOK
# =================================================================

# Получаем токен из переменной окружения (как настроено на Render)
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Переменная окружения 'BOT_TOKEN' не найдена.")

# Параметры Webhook. Render сам заполнит эти переменные.
# WEBHOOK_HOST - имя твоего сайта (например, my-tg-bot.onrender.com)
WEBHOOK_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME') 
WEBHOOK_PATH = f'/webhook/{TOKEN}' # Уникальный путь для безопасности
WEBHOOK_URL = f'https://{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки веб-сервера
WEBAPP_HOST = '0.0.0.0' # Слушаем все интерфейсы
WEBAPP_PORT = int(os.environ.get('PORT', 8080)) # Порт, который дает Render

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =================================================================
# 2. ОБРАБОТЧИКИ КОМАНД (ЛОГИКА БОТА)
# =================================================================

@dp.message(CommandStart())
async def handle_start(message: Message):
    """Отвечает на команду /start"""
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n"
        "Я бот, запущенный на Render через Webhook. Отправь мне что-нибудь!"
    )

@dp.message()
async def handle_echo(message: Message):
    """Отвечает на любое сообщение, просто повторяя его"""
    await message.answer(f"Я получил твое сообщение: **{message.text}**")


# =================================================================
# 3. ФУНКЦИИ УПРАВЛЕНИЯ WEBHOOK
# =================================================================

async def on_startup(app):
    """Вызывается при запуске сервера: устанавливает Webhook"""
    logging.info(f"Устанавливаю Webhook на URL: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)
    
async def on_shutdown(app):
    """Вызывается при остановке сервера: удаляет Webhook"""
    logging.info("Удаляю Webhook...")
    await bot.delete_webhook()
    await bot.session.close()

async def webhook_handler(request):
    """Обрабатывает входящие POST-запросы от Telegram"""
    if request.match_info.get('token') == TOKEN:
        # Получаем и обрабатываем данные
        update_data = await request.json()
        update = Update.model_validate(update_data, context={'bot': bot})
        
        await dp.feed_update(bot, update)
        
        return web.Response()
    else:
        return web.Response(status=403) # 403 Forbidden - ошибка токена
        
# =================================================================
# 4. ЗАПУСК ПРИЛОЖЕНИЯ
# =================================================================

if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Регистрируем обработчик по пути WEBHOOK_PATH
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    
    logging.info(f"Запуск веб-сервера на {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
