import datetime

from aiogram import types


async def timedelta_from_msg(message: types.Message):
    duration = message.text.split(' ')

    if len(duration) == 2:
        modifiers = {
            "w": datetime.timedelta(weeks=1),
            "d": datetime.timedelta(days=1),
            "h": datetime.timedelta(hours=1),
            "m": datetime.timedelta(minutes=1),
            "s": datetime.timedelta(seconds=30),
            "p": datetime.timedelta(weeks=999)
        }

        if duration[-1].isdigit():

            if int(duration[-1]) < 30:
                return datetime.timedelta(seconds=30)

            else:
                return datetime.timedelta(seconds=int(duration[-1]))

        elif duration[-1].isalpha():
            return modifiers.get(duration[-1], datetime.timedelta(minutes=15))

        else:
            return datetime.timedelta(minutes=15)

    else:
        return datetime.timedelta(minutes=15)
