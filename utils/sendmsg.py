from datetime import date

from aiogram import Dispatcher

from db.models import CountMembers


async def send_shedule_messages(dp: Dispatcher):
    db_session = dp.bot.get('db')
    today_is = f'{date.today().day}{date.today().month}{date.today().year}'

    async with db_session() as ssn:
        today_stats: CountMembers = await ssn.get(CountMembers, today_is)

    await dp.bot.send_message(-1001655542688, f'За сегодня:\nПрисоединились {today_stats.joined}\nВышли {today_stats.left}')
