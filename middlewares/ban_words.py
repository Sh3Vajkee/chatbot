import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler


class NotAllowedWords(BaseMiddleware):

    async def on_process_message(self, m: types.Message, data: dict):

        words = ['жопа', 'хуй']

        if m.text:
            msg_text = m.text.lower()

            for word in words:

                if word in msg_text:
                    await m.bot.delete_message(m.chat.id, m.message_id)
                    logging.info(
                        f'Удалено сообщение от пользователя {m.from_user.mention}\nТекст сообщения:\n{m.text}')
                    raise CancelHandler()

        else:
            return
