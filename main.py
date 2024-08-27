import asyncio
from datetime import datetime, timedelta
from typing import Union

from aiogram import Bot, Dispatcher, types, filters
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app import config, database

props = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=config.BOT_TOKEN, default=props)
dp = Dispatcher()


UTC_OFFSET = 3


@dp.message(filters.CommandStart())
async def start_timer(message: types.Message):
    text = [
        "Ну привет, серунишка 😏",
        "",
        "Меня зовут SORTIRO, и я твой личный трекер времени, проведенного за очень важным делом 🚽",
        "",
        "Отправь:",
        "/start_timer - когда начнешь 💩",
        "/stop_timer - когда закончишь 💩",
        "/day_stat - чтобы посмотреть потраченное время за сегодня",
        "/week_stat - чтобы посмотреть потраченное время за неделю",
        "/month_stat - чтобы посмотреть потраченное время за месяц",
        "/all_stat - чтобы посмотреть потраченное время за все время",
    ]
    await message.reply("\n".join(text))


@dp.message(filters.Command("start_timer"))
async def start_timer(message: types.Message):
    user_id = message.from_user.id
    timer = database.get_timer(user_id=user_id)
    if timer:
        await message.reply(
            "Ты уже в процессе 💩\nЕсли хочешь остановить таймер, отправь /stop_timer"
        )
    else:
        start_time = datetime.now()
        database.create_timer(user_id=user_id, start_time=start_time)
        await message.reply("Пошел процесс 💩")


@dp.message(filters.Command("stop_timer"))
async def stop_timer(message: types.Message):
    user_id = message.from_user.id
    timer = database.get_timer(user_id=user_id)
    if timer:
        start_time = datetime.fromisoformat(timer[0])
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        database.stop_timer(user_id=user_id, end_time=end_time, duration=duration)
        await message.reply(
            f"С облегчением! 😏\nПотраченное время: {timedelta(seconds=duration)}."
        )
    else:
        await message.reply(
            "Ты же не начинал процесс?😳\nЧтобы начать, отправь /start_timer"
        )


@dp.message(filters.Command("day_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = datetime.now() - timedelta(days=1) + timedelta(hours=UTC_OFFSET)
    stats = get_stat(user_id=user_id, period=start_period)
    stats.insert(0, "📈<b>Статистика за день</b>\n")
    await message.reply("\n".join(stats))


@dp.message(filters.Command("week_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = datetime.now() - timedelta(weeks=1) + timedelta(hours=UTC_OFFSET)
    stats = get_stat(user_id=user_id, period=start_period)
    stats.insert(0, "📈<b>Статистика за неделю</b>\n")
    await message.reply("\n".join(stats))


@dp.message(filters.Command("month_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = datetime.now() - timedelta(days=30) + timedelta(hours=UTC_OFFSET)
    stats = get_stat(user_id=user_id, period=start_period)
    stats.insert(0, "📈<b>Статистика за месяц</b>\n")
    await message.reply("\n".join(stats))


@dp.message(filters.Command("all_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = None
    stats = get_stat(user_id=user_id, period=start_period)
    stats.insert(0, "📈<b>Статистика за все время</b>\n")
    await message.reply("\n".join(stats))


def get_stat(user_id: int, period: Union[datetime, None]):
    if period:
        stat = database.get_stat_by_period(user_id=user_id, period=period)
    else:
        stat = database.get_stats(user_id=user_id)
    if stat:
        duration, count = stat

    duration, count = duration if duration else 0, count if count else 0
    average_time = str(
        timedelta(seconds=duration / count) if count > 0 else timedelta(seconds=0)
    ).split(".")[0]

    return [
        f"⌚Потраченное время: {timedelta(seconds=duration)}.",
        f"🔄️Ты облегчался: {count} {pluralization(count)}.",
        f"📊Среднее время: {average_time}.",
    ]


def pluralization(count: int):
    if count < 20:
        if count <= 1 or count >= 5:
            return "раз"
        else:
            return "раза"
    new_count = int(str(count)[-1])
    return pluralization(new_count)


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
