import logging
from random import shuffle
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter, Text

from db.models import ChatgroupUser
from middlewares.throttling import rate_limit
from keyboars import join_kb


@rate_limit("default")
async def cmd_start(message: types.Message):
    await message.answer(
        'Читайте правила группы:\n\n/rules'
    )


@rate_limit("default")
async def cmd_rules(message: types.Message):
    db_sesion = message.bot.get('db')

    async with db_sesion() as session:
        usr: ChatgroupUser = await session.get(ChatgroupUser, message.from_user.id)

    rules_text = '1. Правило_1\n2. Правило_2\n3. Правило_3\n4. Правило_4\n5. Правило_5 Ответ: лимон\n6. Правило_6'

    if not usr.checked:

        rules_text += '\n\nНажмите на кнопку ниже для проверки и получения доступа к чату.'
        await message.answer(rules_text, reply_markup=join_kb)

    else:
        await message.answer(rules_text)


async def test_permissions(call: types.CallbackQuery):

    check_test_btns = [
        types.InlineKeyboardButton('🍋', callback_data='test_right'),
        types.InlineKeyboardButton('🍊', callback_data='test_fail'),
        types.InlineKeyboardButton('🍏', callback_data='test_fail'),
        types.InlineKeyboardButton('🍐', callback_data='test_fail'),
        types.InlineKeyboardButton('🍑', callback_data='test_fail'),
        types.InlineKeyboardButton('🍓', callback_data='test_fail')
    ]

    shuffle(check_test_btns)
    check_text = types.InlineKeyboardMarkup(
        row_width=3).add(*check_test_btns)

    await call.message.edit_text('Выберите ответ на контрольный вопрос. Если выбор будет неправильный, вы будете кикнуты.',
                                 reply_markup=check_text)


async def test_btn(call: types.CallbackQuery):

    if call.data.split('_')[-1] == 'fail':

        await call.bot.unban_chat_member(-1001655542688, call.from_user.id)
        await call.message.answer('Вы ответили неправильно и были кикнуты из группы!')
        await call.message.delete()

    else:

        await call.bot.restrict_chat_member(
            -1001655542688,
            call.from_user.id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True
        )
        await call.message.answer('Теперь вы можете писать в чат группы!')
        await call.message.delete()

        logging.info(
            f'User {call.from_user.mention} with id:{call.from_user.id} now can send messages'
        )

        db_session = call.bot.get('db')

        async with db_session() as session:
            usr: ChatgroupUser = await session.get(ChatgroupUser, call.from_user.id)
            usr.checked = True
            await session.commit()


def get_perm_handlers(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        commands='start'
    )
    dp.register_message_handler(
        cmd_rules,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        commands='rules'
    )
    dp.register_callback_query_handler(
        test_permissions,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        text='join_ok'
    )
    dp.register_callback_query_handler(
        test_btn,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        Text(startswith='test_')
    )
