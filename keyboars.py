from aiogram import types

join_kb = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton('Получить доступ', callback_data='join_ok'))

test_kb = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton('OK', url='tg://openmessage?user_id=5265116040'))
