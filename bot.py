import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# === 🔑 Укажи свои данные ===
TOKEN = "7504680458:AAHPQowdVf0OC0l-sSP-gA8exyGKHElQVPI"
WEATHER_API_KEY = "55dfe164f52d5a0d296b486466a7a0fa"
CHAT_ID = "1951583388"  # ID пользователя или группы
CITY = "Санкт-Петербург"  # Город для прогноза

# === 🔥 Настраиваем бота ===
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# === 🌤️ Функция получения погоды ===
async def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["main"]["temp"]
                weather_desc = data["weather"][0]["description"]
                return f"Сейчас в {city}: {temp}°C, {weather_desc}"
            else:
                return "Не удалось получить погоду 😔"

# === 🕒 Функция ежедневной отправки погоды ===
async def send_daily_weather():
    while True:
        try:
            weather = await get_weather(CITY)
            await bot.send_message(CHAT_ID, f"Доброе утро! 🌞\n{weather}")

            # Отправляем видео котика
            API_KEY = "live_gM1zOn6z760Gh8qtj8nH5lyyRYY356PKrY5aHnVLeCmdT74x8eIi61h7chji66ab"  # Получи ключ на thecatapi.com
CHAT_ID = "1951583388"
CITY = "Санкт-Петербург"

async def get_random_cat_video():
    url = "https://api.thecatapi.com/v1/images/search?mime_types=video/mp4"
    headers = {"x-api-key": API_KEY}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data:
                    return data[0]["url"]  # Получаем ссылку на видео
            return None

async def send_daily_weather():
    while True:
        try:
            weather = await get_weather(CITY)
            await bot.send_message(CHAT_ID, f"Доброе утро! 🌞\n{weather}")

            cat_video = await get_random_cat_video()
            if cat_video:
                await bot.send_video(CHAT_ID, cat_video)
            else:
                await bot.send_message(CHAT_ID, "Сегодня без котика 😿")

            await asyncio.sleep(86400)  # Ждём 24 часа
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await asyncio.sleep(60)  # Если ошибка, ждём 1 минуту

            await asyncio.sleep(86400)  # Ждём 24 часа (86400 секунд)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await asyncio.sleep(60)  # Если ошибка, ждём 1 минуту

# === 📩 Обработчик команды /start ===
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Я буду каждый день присылать погоду и видео котика! 🐱🌤️")

# === 🚀 Запуск бота ===
async def main():
    asyncio.create_task(send_daily_weather())  # Запускаем задачу отправки погоды
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())