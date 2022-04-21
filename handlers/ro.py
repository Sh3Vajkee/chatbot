import logging
from babel.dates import format_timedelta

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command, ChatTypeFilter
from aiogram.utils.exceptions import BadRequest

from utils.timedelta import timedelta_from_msg
from filters.player_filter import IsAdmin
from db.models import ChatgroupUser


async def ro_user(message: types.Message):
    user_id = message.reply_to_message.from_user.id

    duration = await timedelta_from_msg(message)

    if not duration:
        return

    try:
        await message.chat.restrict(
            user_id=user_id,
            can_send_messages=False,
            until_date=duration
        )
        logging.info(
            f'User {user_id} restricted by {message.from_user.id} for {duration}')
    except BadRequest as e:
        logging.info('Failed to restrict chat member: {error!r}', error=e)
        return False

    usr_name = message.reply_to_message.from_user.get_mention()
    duration = format_timedelta(
        duration, granularity="seconds", format="short")

    await message.reply_to_message.answer(f"<b>Read-only</b> активирован для пользователя {usr_name}. Длительность: {duration}")
    await message.bot.send_message(user_id, f"Вы помещены в <b>Read-only</b> в группе. Длительность: {duration}")

    db_session = message.bot.get('db')

    async with db_session() as session:
        usr: ChatgroupUser = await session.get(ChatgroupUser, user_id)
        usr.warn_count += 1
        await session.commit()

    return True


async def ban_user(message: types.Message):
    user_id = message.reply_to_message.from_user.id

    duration = await timedelta_from_msg(message)

    if not duration:
        return

    try:
        await message.chat.kick(
            user_id=user_id,
            until_date=duration
        )
        logging.info(
            f'User {user_id} kicked by {message.from_user.id} for {duration}')
    except BadRequest as e:
        logging.info('Failed to kick chat member: {error!r}', error=e)
        return False

    usr_name = message.reply_to_message.from_user.get_mention()
    duration = format_timedelta(
        duration, granularity="seconds", format="short")

    await message.reply_to_message.answer(f"{usr_name} был кикнут из чата на {duration}")
    await message.bot.send_message(user_id, f"Вы были кикнуты из чата на {duration}")

    db_session = message.bot.get('db')

    async with db_session() as session:
        usr: ChatgroupUser = await session.get(ChatgroupUser, user_id)
        usr.ban_count += 1
        usr.checked = False
        await session.commit()

    return True


def ro_handlers(dp: Dispatcher):
    dp.register_message_handler(
        ro_user, ChatTypeFilter(chat_type=[types.ChatType.GROUP,
                                           types.ChatType.SUPERGROUP, ]), IsAdmin(), Command('ro', prefixes='!'))
    dp.register_message_handler(
        ban_user, ChatTypeFilter(chat_type=[types.ChatType.GROUP,
                                            types.ChatType.SUPERGROUP, ]), IsAdmin(), Command('ban', prefixes='!'))
