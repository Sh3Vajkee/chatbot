import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.utils.markdown import hlink
from middlewares.throttling import rate_limit


@rate_limit("default")
async def report_user(message: types.Message):
    logging.info(
        f"User {message.from_user.id} report message {message.message_id} in chat from user {message.reply_to_message.from_user.id}"
    )

    if not message.reply_to_message:
        return await message.reply("Reply message what you want to report")

    chat = hlink(message.chat.title,
                 f'https://t.me/{message.chat.title}/{message.reply_to_message.message_id}')
    text = f"[ALERT] User {message.from_user.id} is reported message in chat {chat}."

    await message.bot.send_message(746461090, text)


def report_handlers(dp: Dispatcher):
    dp.register_message_handler(report_user, ChatTypeFilter(chat_type=[types.ChatType.GROUP,
                                                                       types.ChatType.SUPERGROUP, ]), Command('report', prefixes='!/'))
