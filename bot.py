import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# --- Настройки ---
TOKEN = "7504680458:AAHPQowdVf0OC0l-sSP-gA8exyGKHElQVPI"
WEATHER_API_KEY = "55dfe164f52d5a0d296b486466a7a0fa"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
CAT_GIF_URL = "https://cataas.com/cat/gif"

# --- Логирование ---
logging.basicConfig(level=logging.INFO)

# --- Инициализация бота ---
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- Хранение данных о пользователях ---
user_cities = {}

# --- Клавиатура ---
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Установить город 🌍"))

# --- Функция получения погоды ---
async def get_weather(city):
    async with aiohttp.ClientSession() as session:
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": "ru"}
        async with session.get(WEATHER_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"🌤 Погода в *{city}*: {temp}°C, {desc}"
            else:
                return None

# --- Функция получения GIF котика ---
async def get_cat_gif():
    return CAT_GIF_URL  # Сайт Cataas всегда даёт новое GIF-изображение кота

# --- Команда /start ---
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я твой погодный кото-бот! 🐱🌤\nВыбери город, чтобы я каждый день присылал тебе прогноз.", reply_markup=keyboard)

# --- Установка города ---
@dp.message_handler(lambda message: message.text == "Установить город 🌍")
async def set_city(message: types.Message):
    await message.answer("Введите название города:")

@dp.message_handler()
async def save_city(message: types.Message):
    user_cities[message.from_user.id] = message.text
    await message.answer(f"Отлично! Теперь я буду присылать тебе погоду в *{message.text}* каждый день. 🐱")

# --- Рассылка погоды каждый день ---
async def daily_weather():
    while True:
        for user_id, city in user_cities.items():
            weather = await get_weather(city)
            cat_gif = await get_cat_gif()
            if weather:
                await bot.send_message(user_id, weather, parse_mode="Markdown")
                await bot.send_animation(user_id, cat_gif)
        await asyncio.sleep(86400)  # Раз в 24 часа

# --- Запуск бота ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(daily_weather())
    executor.start_polling(dp, skip_updates=True)