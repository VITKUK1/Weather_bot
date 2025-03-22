import asyncio
import logging
import aiohttp
import datetime
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# === 🔑 API-ключи ===
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
CAT_API_KEY = "YOUR_THECATAPI_KEY"

# === 🔥 Настройка бота ===
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

user_data = {}
weather_tasks = {}

# === 🐱 Резервное видео котика ===
FALLBACK_CAT_VIDEO = "BAACAgIAAxkBAAIBWmYl9TzhxX-2U5lq8u9eXyprlJXRAAItJQAC7_kRS-3FlXJJZ-YjNAQ"

# === ☀️ Стикеры погоды ===
STICKERS = {
    "clear": "CAACAgIAAxkBAAEIfwpkQvYFzB_SmF0aKjo4i3hoZazfwAACIAADwDZPE8vUhzQQD2UgNAQ",  # ☀️
    "rain": "CAACAgIAAxkBAAEIfw1kQvYOMOS7WJnt7vExjcF9Rxjj7QACJQADwDZPE9CUwGRlR08GNAQ",  # 🌧
    "clouds": "CAACAgIAAxkBAAEIfxBkQvYV02-HE9nLk8loCrmRfQgFNQACJAADwDZPE9qXENj4PzJRNAQ"  # ☁️
}

# === 🕒 Функция получения часового пояса ===
async def get_timezone(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                timezone_offset = data["timezone"]
                return pytz.FixedOffset(timezone_offset // 60)
            return None

# === 🕒 Ожидание 9 утра ===
async def wait_until_9am(city):
    timezone = await get_timezone(city)
    if not timezone:
        return

    now = datetime.datetime.now(timezone)
    next_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)

    if now >= next_9am:
        next_9am += datetime.timedelta(days=1)

    wait_time = (next_9am - now).total_seconds()
    await asyncio.sleep(wait_time)

# === 🐱 Функция получения видео котика ===
async def get_random_cat_video():
    url = "https://api.thecatapi.com/v1/images/search?mime_types=video/mp4"
    headers = {"x-api-key": CAT_API_KEY}

    for _ in range(10):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data:
                            if item.get("url", "").endswith(".mp4"):
                                return item["url"]
            except Exception:
                pass
        await asyncio.sleep(1)

    return None

# === 🌤️ Получение погоды ===
async def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["main"]["temp"]
                weather_desc = data["weather"][0]["description"]
                weather_main = data["weather"][0]["main"].lower()
                
                # Определяем стикер по погоде
                if "clear" in weather_main:
                    sticker = STICKERS["clear"]
                elif "rain" in weather_main:
                    sticker = STICKERS["rain"]
                elif "cloud" in weather_main:
                    sticker = STICKERS["clouds"]
                else:
                    sticker = None

                return f"Сейчас в {city}: {temp}°C, {weather_desc}", sticker
            return "Не удалось получить погоду 😔", None

# === 🕒 Функция отправки погоды ===
async def send_daily_weather(user_id, city):
    while True:
        try:
            await wait_until_9am(city)

            weather_text, weather_sticker = await get_weather(city)
            await bot.send_message(user_id, f"Доброе утро! 🌞\n{weather_text}")

            # Отправляем стикер, если найден
            if weather_sticker:
                await bot.send_sticker(user_id, weather_sticker)

            cat_video = await get_random_cat_video()
            if cat_video:
                await bot.send_video(user_id, cat_video)
            else:
                await bot.send_video(user_id, FALLBACK_CAT_VIDEO)

        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(60)

# === 🚀 Запуск задачи с погодой ===
async def start_weather_task(user_id, city):
    if user_id in weather_tasks and not weather_tasks[user_id].done():
        return

    weather_tasks[user_id] = asyncio.create_task(send_daily_weather(user_id, city))

# === 🎛 Обработчик /start ===
@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    if user_id in user_data:
        await message.answer(f"Ты уже выбрал город: {user_data[user_id]}.\nПогода будет приходить в 9 утра!")
        return

    await message.answer("Привет! Введи название города 🌍")

# === 📩 Обработчик ввода города ===
@dp.message()
async def set_city(message: Message):
    user_id = message.from_user.id
    city = message.text.strip()

    timezone = await get_timezone(city)
    if not timezone:
        await message.answer("Не удалось определить город. Попробуй ещё раз 🏙")
        return

    user_data[user_id] = city
    await message.answer(f"Отлично! Теперь я буду отправлять погоду для {city} в 9 утра ⏰")
    await start_weather_task(user_id, city)

# === 🚀 Запуск бота ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())