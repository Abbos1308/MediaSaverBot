import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config.settings import BOT_TOKEN, ADMIN_ID
from bot.database.models import db
from bot.database.queries import is_admin
from bot.middlewares.admin import AdminMiddleware
from bot.handlers import user, admin
from bot.middlewares.throttling import ThrottlingMiddleware


logging.basicConfig(level=logging.INFO)

async def initialize_admin():
    async with db.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO admins (user_id) VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
        ''', ADMIN_ID)

async def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN is not set in environment variables!")
        return
    
    if ADMIN_ID == 0:
        logging.error("ADMIN_ID is not set in environment variables!")
        return
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    await db.connect()
    await initialize_admin()
    
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.5))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=1.5))

    dp.include_router(user.router)
    dp.include_router(admin.router)
    
    logging.info("Bot started successfully!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())