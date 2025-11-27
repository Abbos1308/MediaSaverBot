# throttling.py
import asyncio
import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        """
        rate_limit: minimum seconds between requests per user
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.last_time = {}  # user_id -> timestamp

    async def __call__(self, handler, event, data):
        # Works for both messages and callbacks
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            now = time.monotonic()
            last = self.last_time.get(user_id, 0)
            if now - last < self.rate_limit:
                # Too fast → ignore or send warning
                if isinstance(event, Message):
                    await event.answer("⏳ Please wait before sending again.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⏳ Slow down!", show_alert=False)
                return  # stop handler
            self.last_time[user_id] = now

        return await handler(event, data)