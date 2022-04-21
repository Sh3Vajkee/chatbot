from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from db.models import ChatgroupUser


class CorrectMsg(BoundFilter):
    key = 'correct_msg'

    async def check(self, call: types.CallbackQuery):
        db_session = call.bot.get('db')

        async with db_session() as session:
            user: ChatgroupUser = await session.get(ChatgroupUser, call.from_user.id)

        return user.msg_id == call.message.message_id


class IsPrivate(BoundFilter):
    key = 'is_private'

    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE


class IsAdmin(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message):
        admins = [746461090]
        return message.from_user.id in admins
