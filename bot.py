import asyncio
import logging
import aiohttp
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

# === 🐱 Резервное видео котика ===
FALLBACK_CAT_VIDEO = "BAACAgIAAxkBAAIBWmYl9TzhxX-2U5lq8u9eXyprlJXRAAItJQAC7_kRS-3FlXJJZ-YjNAQ"

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

# === 🐱 Функция получения видео котика ===
async def get_random_cat_video():
    url = "https://api.thecatapi.com/v1/images/search?mime_types=video/mp4"
    headers = {"x-api-key": CAT_API_KEY}
    
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

    return None  # Если видео нет, возвращаем None

# === 🕒 Функция отправки погоды (учитывает город) ===
async def send_daily_weather(user_id, city):
    while True:
        try:
            weather = await get_weather(city)
            await bot.send_message(user_id, f"Доброе утро! 🌞\n{weather}")

            cat_video = await get_random_cat_video()
            if cat_video:
                await bot.send_video(user_id, cat_video)
            else:
                await bot.send_video(user_id, FALLBACK_CAT_VIDEO)

            await asyncio.sleep(86400)  # Ждём 24 часа
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

# === 🛑 Остановка погоды ===
async def stop_weather(user_id):
    if user_id in weather_tasks:
        weather_tasks[user_id].cancel()
        del weather_tasks[user_id]

# === 📩 Обработчик команды /start (клавиатура с кнопкой) ===
@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Перезапуск бота")]
        ],
        resize_keyboard=True
    )

    if user_id in user_data:
        await message.answer(f"Ты уже выбрал город: {user_data[user_id]} 🌍", reply_markup=keyboard)
        await start_weather_task(user_id, user_data[user_id])
    else:
        await message.answer("Привет! В каком ты городе? 🌍 Напиши название города.", reply_markup=keyboard)

# === 🌎 Обработчик ответа с городом ===
@dp.message(lambda message: message.from_user.id not in user_data and message.text != "Перезапуск бота")
async def set_city(message: Message):
    user_id = message.from_user.id
    city = message.text.strip()

    user_data[user_id] = city  # Сохраняем город
    await message.answer(f"Отлично! Буду показывать погоду в {city}. 🌤️")
    await start_weather_task(user_id, city)

# === 🔄 Обработчик кнопки "Перезапуск бота" ===
@dp.message(lambda message: message.text == "Перезапуск бота")
async def restart_bot(message: Message):
    user_id = message.from_user.id

    await stop_weather(user_id)  # Останавливаем отправку погоды
    if user_id in user_data:
        del user_data[user_id]  # Сбрасываем город

    await message.answer("🔄 Бот перезапущен! В каком ты городе? 🌍 Напиши название города.")

# === 🛑 Обработчик команды 'стоп' ===
@dp.message(lambda message: message.text.lower() == "стоп")
async def stop_weather_command(message: Message):
    user_id = message.from_user.id
    await stop_weather(user_id)
    await message.answer("Бот остановлен! ❌")

# === 🚀 Запуск бота ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())