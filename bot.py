import asyncio
import logging
import aiohttp
import datetime
import pytz  # Для работы с часовыми поясами
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# === 🔑 API-ключи ===
TOKEN = "7504680458:AAHPQowdVf0OC0l-sSP-gA8exyGKHElQVPI"
WEATHER_API_KEY = "55dfe164f52d5a0d296b486466a7a0fa"
CAT_API_KEY = "live_gM1zOn6z760Gh8qtj8nH5lyyRYY356PKrY5aHnVLeCmdT74x8eIi61h7chji66ab"

# === 🔥 Настройка бота ===
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Храним данные пользователей (ID -> город)
user_data = {}
weather_tasks = {}

# === 🐱 Резервное видео котика (Telegram File ID) ===
FALLBACK_CAT_VIDEO = "BAACAgIAAxkBAAIBWmYl9TzhxX-2U5lq8u9eXyprlJXRAAItJQAC7_kRS-3FlXJJZ-YjNAQ"

# === ⏳ Функция получения часового пояса по городу ===
async def get_timezone(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                timezone_offset = data["timezone"]  # Смещение в секундах
                return pytz.FixedOffset(timezone_offset // 60)  # Переводим в часовой пояс
            else:
                return None

# === 🕒 Функция ожидания 9 утра по местному времени ===
async def wait_until_9am(city):
    timezone = await get_timezone(city)
    if not timezone:
        logging.error(f"Не удалось получить часовой пояс для {city}")
        return

    now = datetime.datetime.now(timezone)
    next_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)

    if now >= next_9am:  # Если уже прошло 9 утра, ждём до завтра
        next_9am += datetime.timedelta(days=1)

    wait_time = (next_9am - now).total_seconds()
    logging.info(f"Ждём {wait_time / 60:.2f} минут до 9 утра в городе {city}")
    await asyncio.sleep(wait_time)

# === 🐱 Функция получения видео котика ===
async def get_random_cat_video():
    url = "https://api.thecatapi.com/v1/images/search?mime_types=video/mp4"
    headers = {"x-api-key": CAT_API_KEY}

    for _ in range(3):  # Пробуем 3 раза
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data:
                            if item.get("url", "").endswith(".mp4"):  # Проверяем, что это видео
                                return item["url"]
            except Exception as e:
                logging.error(f"Ошибка при получении видео котика: {e}")
        
        await asyncio.sleep(1)  # Ждём 1 секунду перед повтором

    return None  # Если видео нет, возвращаем None

# === 🌤️ Функция получения погоды ===
async def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["main"]["temp"]
                weather_desc = data["weather"][0]["description"]
                return f"Сейчас в {city}: {temp}°C, {weather_desc}"
            else:
                return "Не удалось получить погоду 😔"

# === 🕒 Функция отправки погоды ===
async def send_daily_weather(user_id, city):
    while True:
        try:
            await wait_until_9am(city)  # Ждём 9 утра по городу

            weather = await get_weather(city)
            await bot.send_message(user_id, f"Доброе утро! 🌞\n{weather}")

            cat_video = await get_random_cat_video()
            if cat_video:
                try:
                    await bot.send_video(user_id, cat_video)
                except Exception as e:
                    logging.error(f"Ошибка при отправке видео котика: {e}")
                    await bot.send_video(user_id, FALLBACK_CAT_VIDEO)
            else:
                await bot.send_video(user_id, FALLBACK_CAT_VIDEO)

        except asyncio.CancelledError:
            logging.info(f"Задача отправки погоды для {user_id} остановлена.")
            break
        except Exception as e:
            logging.error(f"Ошибка у {user_id}: {e}")
            await asyncio.sleep(60)

# === 🚀 Функция запуска задачи с погодой ===
async def start_weather_task(user_id, city):
    if user_id in weather_tasks and not weather_tasks[user_id].done():
        return  # Если задача уже запущена, не запускаем повторно

    weather_tasks[user_id] = asyncio.create_task(send_daily_weather(user_id, city))

# === 🚀 Запуск бота ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())