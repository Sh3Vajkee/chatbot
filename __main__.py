import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats, BotCommandScopeAllChatAdministrators, BotCommandScopeChatAdministrators
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config_loader import Config, load_config
from db.base import Base
from middlewares.throttling import ThrottlingMiddleware
from middlewares.ban_words import NotAllowedWords
from handlers.chat_member import new_member_handlers
from handlers.get_perm import get_perm_handlers
from handlers.ro import ro_handlers
from handlers.report import report_handlers
from handlers.user_commands import user_commands_handlers
from utils.sendmsg import send_shedule_messages
from updatesworker import get_handled_updates_list


async def set_bot_commands(bot: Bot):
    commands_group = [
        BotCommand(command="followage",
                   description="Время пребывания в группе"),
        BotCommand(command="iq", description="iq")
    ]

    commands_group_admin = [
        BotCommand(command="kekw", description="kekw"),
        BotCommand(command="followage",
                   description="Время пребывания в группе"),
        BotCommand(command="iq", description="iq"),
        BotCommand(command='check_user', description='user info')
    ]

    commands_private = [
        BotCommand(command="start", description="start"),
        BotCommand(command="rules", description="rules"),
        BotCommand(command="stats", description="stats"),
    ]

    commands_private_admin = [
        BotCommand(command="start", description="start"),
        BotCommand(command="rules", description="rules"),
        BotCommand(command="stats", description="stats"),
    ]

    await bot.set_my_commands(commands_group, scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(commands_private, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands_group_admin, scope=BotCommandScopeAllChatAdministrators())
    # await bot.set_my_commands(commands_private_admin, scope=BotCommandScopeChatAdministrators())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    config: Config = load_config()

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    storage = MemoryStorage()
    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    dp = Dispatcher(bot, storage=storage)

    sheduler = AsyncIOScheduler()
    # sheduler.add_job(send_shedule_messages, 'interval',
    #                  minutes=1, args=(dp,))
    sheduler.add_job(
        send_shedule_messages,
        'cron',
        hour='23',
        minute='59',
        second='59',
        args=(dp,)
    )
    sheduler.start()

    dp.middleware.setup(NotAllowedWords())
    dp.middleware.setup(ThrottlingMiddleware())

    new_member_handlers(dp)
    get_perm_handlers(dp)
    ro_handlers(dp)
    report_handlers(dp)
    user_commands_handlers(dp)

    await set_bot_commands(bot)

    try:
        await dp.skip_updates()
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
