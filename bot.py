import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# === 🔑 Укажи свои данные ===
TOKEN = "ТВОЙ_ТОКЕН"
WEATHER_API_KEY = "ТВОЙ_КЛЮЧ_ПОГОДЫ"
CHAT_ID = "ТВОЙ_CHAT_ID"  # ID пользователя или группы
CITY = "Москва"  # Город для прогноза

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
            cat_video = "https://example.com/cat.mp4"  # Замени на реальную ссылку
            await bot.send_video(CHAT_ID, cat_video)

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