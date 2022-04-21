import asyncio
import logging
from datetime import datetime, date
from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.utils.exceptions import MessageToDeleteNotFound

from keyboars import test_kb
from db.models import ChatgroupUser, CountMembers


async def user_join(message: types.Message):

    await message.bot.restrict_chat_member(
        message.chat.id,
        message.new_chat_members[0].id,
        can_send_messages=False
    )

    chat_id = message.chat.id
    user = message.new_chat_members[0]

    bot_user = await message.bot.get_me()
    bot_username = bot_user.username

    msg = await message.bot.send_message(
        chat_id,
        f'Приветствую в группе, {user.mention}!\n'
        'Чтобы получить возможность писать в чат, необходимо ознакомиться с правилами группы\n'
        f'Для этого необходимо написать боту @{bot_username}\nИли нажать кнопку ниже',
        reply_markup=test_kb
    )

    db_session = message.bot.get('db')

    async with db_session() as session:
        await session.merge(
            ChatgroupUser(
                user_id=user.id,
                user_name=user.mention,
                checked=False,
                join_date=datetime.now().timestamp()
            )
        )

        today_is = f'{date.today().day}{date.today().month}{date.today().year}'
        count: CountMembers = await session.get(CountMembers, today_is)

        if count:
            count.joined += 1
        else:
            await session.merge(
                CountMembers(
                    id=today_is,
                    day=date.today().day,
                    month=date.today().month,
                    year=date.today().year,
                    joined=1,
                    left=0
                )
            )
        await session.commit()

    await asyncio.sleep(5)
    with suppress(MessageToDeleteNotFound):
        await message.bot.delete_message(chat_id, msg.message_id)

    logging.info(
        f'User {message.new_chat_members[0].mention} with id:{user.id} joined.'
    )


async def user_left(message: types.Message):
    db_session = message.bot.get('db')

    async with db_session() as ssn:
        usr: ChatgroupUser = await ssn.get(ChatgroupUser, message.left_chat_member.id)
        usr.leave_date = datetime.now().timestamp()

        today_is = f'{date.today().day}{date.today().month}{date.today().year}'
        count: CountMembers = await ssn.get(CountMembers, today_is)

        if count:
            count.left += 1
        else:
            await ssn.merge(
                CountMembers(
                    id=today_is,
                    day=date.today().day,
                    month=date.today().month,
                    year=date.today().year,
                    joined=0,
                    left=1
                )
            )

        await ssn.commit()

    time_delta = str(datetime.now() -
                     datetime.fromtimestamp(usr.join_date)).split(', ')

    if len(time_delta) > 1:
        days = time_delta[0].split()[0]
        hours = time_delta[1][:time_delta[1].index(':')]
    else:
        days = '0'
        hours = time_delta[0][:time_delta[0].index(':')]

    logging.info(
        f'User {message.left_chat_member.mention} with id:{message.left_chat_member.id} left. Был участником чата {days} дней и {hours} часов.'
    )


def new_member_handlers(dp: Dispatcher):
    dp.register_message_handler(
        user_join,
        ChatTypeFilter(
            chat_type=[
                types.ChatType.GROUP,
                types.ChatType.SUPERGROUP,
            ]
        ),
        content_types=types.ContentTypes.NEW_CHAT_MEMBERS
    )
    dp.register_message_handler(
        user_left,
        ChatTypeFilter(
            chat_type=[
                types.ChatType.GROUP,
                types.ChatType.SUPERGROUP,
            ]
        ),
        content_types=types.ContentTypes.LEFT_CHAT_MEMBER
    )
