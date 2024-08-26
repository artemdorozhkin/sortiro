import asyncio
from datetime import datetime, timedelta
from typing import Union

from aiogram import Bot, Dispatcher, types, filters

from app import config, database

bot = Bot(token=config.BOT_TOKEN)
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
    start_period = datetime.now() - timedelta(days=1, hours=UTC_OFFSET)
    duration, count = get_stat(user_id=user_id, period=start_period)
    average_time = (
        timedelta(seconds=duration / count) if count > 0 else timedelta(seconds=0)
    )

    stats = [
        f"⌚Потраченное время за сегодня: {timedelta(seconds=duration)}.",
        f"🔄️Сегодня ты облегчался: {count} {pluralization(count)}.",
        f"📊Среднее время: {average_time}.",
    ]
    await message.reply("\n".join(stats))


@dp.message(filters.Command("week_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = datetime.now() - timedelta(weeks=1, hours=UTC_OFFSET)
    duration, count = get_stat(user_id=user_id, period=start_period)
    average_time = (
        timedelta(seconds=duration / count) if count > 0 else timedelta(seconds=0)
    )

    stats = [
        f"⌚Потраченное время за неделю: {timedelta(seconds=duration)}.",
        f"🔄️На неделе ты облегчался: {count} {pluralization(count)}.",
        f"📊Среднее время: {average_time}.",
    ]
    await message.reply("\n".join(stats))


@dp.message(filters.Command("month_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = datetime.now() - timedelta(days=30, hours=UTC_OFFSET)
    duration, count = get_stat(user_id=user_id, period=start_period)
    average_time = (
        timedelta(seconds=duration / count) if count > 0 else timedelta(seconds=0)
    )

    stats = [
        f"⌚Потраченное время за месяц: {timedelta(seconds=duration)}.",
        f"🔄️За месяц ты облегчался: {count} {pluralization(count)}.",
        f"📊Среднее время: {average_time}.",
    ]
    await message.reply("\n".join(stats))


@dp.message(filters.Command("all_stat"))
async def get_stats(message: types.Message):
    user_id = message.from_user.id
    start_period = None
    duration, count = get_stat(user_id=user_id, period=start_period)
    average_time = (
        timedelta(seconds=duration / count) if count > 0 else timedelta(seconds=0)
    )

    stats = [
        f"⌚Потраченное время за все время: {timedelta(seconds=duration)}.",
        f"🔄️За все время ты облегчался: {count} {pluralization(count)}.",
        f"📊Среднее время: {average_time}.",
    ]
    await message.reply("\n".join(stats))


def get_stat(user_id: int, period: Union[datetime, None]):
    if period:
        stat = database.get_stat_by_period(user_id=user_id, period=period)
    else:
        stat = database.get_stats(user_id=user_id)
    if stat:
        print(stat)
        duration, count = stat

    return duration if duration else 0, count if count else 0


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
