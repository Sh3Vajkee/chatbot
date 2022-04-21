from datetime import datetime, date
from random import randint
from sqlalchemy import select

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter, Text

from db.models import ChatgroupUser, CountMembers
from middlewares.throttling import rate_limit
from filters.player_filter import IsAdmin


@rate_limit("default")
async def followage_cmd(m: types.Message):
    db_session = m.bot.get('db')

    async with db_session() as ssn:
        usr: ChatgroupUser = await ssn.get(ChatgroupUser, m.from_user.id)

    time_delta = str(datetime.now() -
                     datetime.fromtimestamp(usr.join_date)).split(', ')

    if len(time_delta) > 1:
        days = time_delta[0].split()[0]
        hours = time_delta[1][:time_delta[1].index(':')]
    else:
        days = '0'
        hours = time_delta[0][:time_delta[0].index(':')]

    await m.reply(f'Вы в группе уже {days} дней и {hours} часов')


@rate_limit("default")
async def iq_cmd(m: types.Message):
    await m.answer(f'{m.from_user.mention}, твой IQ равен {randint(1, 210)}!')


async def user_info(m: types.Message):
    target_user = m.reply_to_message.from_user.id
    db_session = m.bot.get('db')

    async with db_session() as ssn:
        usr: ChatgroupUser = await ssn.get(ChatgroupUser, target_user)
    await m.answer(
        f'Пользователь {m.reply_to_message.from_user.mention}\n'
        f'ID: {target_user}\n'
        f'Join date: {datetime.fromtimestamp(usr.join_date)}\n'
        f'Мутов: {usr.warn_count}\n'
        f'Банов: {usr.ban_count}\n'
    )


async def cringe_cmd(m: types.Message):
    gif_id = 'CgACAgQAAx0CYq2ToAACBgFiXr5sPXVB12lPkbwJd5Fzw8Qq-QACOgMAAktxtVITW7cdxVRoYCQE'

    if m.reply_to_message:
        await m.bot.send_animation(m.chat.id, gif_id, reply_to_message_id=m.reply_to_message.message_id)

    else:
        await m.bot.send_animation(m.chat.id, gif_id)


async def stats_cmd(m: types.Message):
    db_session = m.bot.get('db')
    today_is = f'{date.today().day}{date.today().month}{date.today().year}'

    async with db_session() as ssn:
        today_stats: CountMembers = await ssn.get(CountMembers, today_is)
        month_s = await ssn.execute(
            select(CountMembers).filter(
                CountMembers.month == date.today().month).filter(CountMembers.year == date.today().year)
        )
        month_stats = month_s.scalars().all()

    if today_stats:
        await m.answer(f'За сегодня: \nПрисоединилось - {today_stats.joined}\nВышло - {today_stats.left}')
    else:
        await m.answer('За сегодня статистика еще не собрана')

    if month_stats:
        month_joined = 0
        month_left = 0
        for day_stat in month_stats:
            month_joined += day_stat.joined
            month_left += day_stat.left

        await m.answer(f'За месяц:\nПрисоединилось - {month_joined}\nВышло - {month_left}')
    else:
        await m.answer('За месяц статистика еще не собрана')


async def check_msg(message: types.Message):
    pass


def user_commands_handlers(dp: Dispatcher):
    dp.register_message_handler(ChatTypeFilter(
        chat_type=[
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP,
        ]
    ), followage_cmd, commands='followage')
    dp.register_message_handler(
        iq_cmd,
        ChatTypeFilter(
            chat_type=[
                types.ChatType.GROUP,
                types.ChatType.SUPERGROUP,
            ]
        ),
        commands='iq'
    )
    dp.register_message_handler(
        ChatTypeFilter(
            chat_type=[
                types.ChatType.GROUP,
                types.ChatType.SUPERGROUP
            ]
        ),
        IsAdmin(),
        user_info,
        commands='check_user'
    )
    dp.register_message_handler(
        stats_cmd,
        IsAdmin(),
        ChatTypeFilter(
            chat_type=[
                types.ChatType.PRIVATE]
        ),
        commands='stats'
    )
    dp.register_message_handler(cringe_cmd, Text(
        equals=['кринж', 'Кринж', 'cringe', 'Cringe']))
    dp.register_message_handler(cringe_cmd, commands=['cringe', 'кринж'])
    dp.register_message_handler(check_msg)
