from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from bot.database.queries import get_all_channels
import logging

async def check_user_subscription(bot: Bot, user_id: int) -> tuple[bool, list]:
    channels = await get_all_channels()
    
    if not channels:
        return True, []
    
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel['channel_id'], user_id=user_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                not_subscribed.append(channel)
        except Exception as e:
            logging.warning(f"Failed to check subscription for channel {channel['channel_id']}: {e}")
            not_subscribed.append(channel)
    
    return len(not_subscribed) == 0, not_subscribed
