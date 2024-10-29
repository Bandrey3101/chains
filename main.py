import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import config
import sched
import time

API_TOKEN = config.token
CHANNEL_1_ID = '@chachachanne'
CHANNEL_2_ID = '@chchchchchchchch1'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

scheduler = sched.scheduler(timefunc=time.time)


# Функция для создания инлайн-кнопки с ссылкой на канал
def create_inline_keyboard(channel_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{channel_id[1:]}")]
    ])
    return keyboard


# Функция для отправки сообщений с задержкой и остановкой по флагу
async def send_messages_with_delay(user_id, messages, stop_flag):
    start_time = time.time()  # Время начала
    for delay, text, channel_id in messages:
        await asyncio.sleep(delay - (time.time() - start_time))  # Задержка с учетом времени
        if stop_flag.is_set():  # Проверка остановки цепочки
            break
        keyboard = create_inline_keyboard(channel_id)
        await bot.send_message(user_id, text, reply_markup=keyboard)


# Цепочки сообщений с контролем остановки
async def start_chain1(user_id, stop_flag1):
    messages = [
        (0, "Цепочка №1: Сообщение №1", CHANNEL_1_ID),
        (300, "Цепочка №1: Сообщение №2", CHANNEL_1_ID),
        (600, "Цепочка №1: Сообщение №3", CHANNEL_1_ID),
        (82800, "Цепочка №1: Сообщение №4", CHANNEL_1_ID),
        (97200, "Цепочка №1: Сообщение №5", CHANNEL_1_ID)
    ]
    await send_messages_with_delay(user_id, messages, stop_flag1)


async def start_chain2(user_id, stop_flag2):
    messages = [
        (0, "Цепочка №2: Сообщение №1", CHANNEL_2_ID),
        (300, "Цепочка №2: Сообщение №2", CHANNEL_2_ID),
        (600, "Цепочка №2: Сообщение №3", CHANNEL_2_ID),
        (82800, "Цепочка №2: Сообщение №4", CHANNEL_2_ID),
        (97200, "Цепочка №2: Сообщение №5", CHANNEL_2_ID)
    ]
    await send_messages_with_delay(user_id, messages, stop_flag2)


# Проверка подписки на каналы с остановкой цепочек
async def check_subscription(user_id, stop_flag1, stop_flag2):
    # Проверка на первый канал
    while True:
        member = await bot.get_chat_member(CHANNEL_1_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            stop_flag1.set()  # Остановка первой цепочки
            asyncio.create_task(start_chain2(user_id, stop_flag2))  # Запуск цепочки 2
            break
        await asyncio.sleep(1)
    # Проверка на второй канал
    while True:
        member = await bot.get_chat_member(CHANNEL_2_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            stop_flag2.set()  # Остановка второй цепочки
            break
        await asyncio.sleep(1)


# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    stop_flag1 = asyncio.Event()  # Флаг для остановки первой цепочки
    stop_flag2 = asyncio.Event()  # Флаг для остановки второй цепочки
    asyncio.create_task(start_chain1(user_id, stop_flag1))  # Запуск цепочки 1
    asyncio.create_task(check_subscription(user_id, stop_flag1, stop_flag2))  # Проверка подписки


if __name__ == "__main__":
    dp.run_polling(bot)
