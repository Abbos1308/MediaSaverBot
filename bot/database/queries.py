from datetime import datetime, timedelta
from bot.database.models import db

async def add_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    async with db.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE
            SET username = $2, first_name = $3, last_name = $4, last_active = CURRENT_TIMESTAMP, is_active = TRUE
        ''', user_id, username, first_name, last_name)

async def update_user_activity(user_id: int):
    async with db.pool.acquire() as conn:
        await conn.execute('''
            UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = $1
        ''', user_id)

async def mark_user_blocked(user_id: int):
    async with db.pool.acquire() as conn:
        await conn.execute('''
            UPDATE users SET is_blocked = TRUE, is_active = FALSE WHERE user_id = $1
        ''', user_id)

async def is_admin(user_id: int) -> bool:
    async with db.pool.acquire() as conn:
        result = await conn.fetchval('SELECT user_id FROM admins WHERE user_id = $1', user_id)
        return result is not None

async def get_all_users():
    async with db.pool.acquire() as conn:
        return await conn.fetch('SELECT user_id FROM users WHERE is_blocked = FALSE')

async def get_stats():
    async with db.pool.acquire() as conn:
        total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
        
        active_users = await conn.fetchval('''
            SELECT COUNT(*) FROM users 
            WHERE last_active >= $1 AND is_blocked = FALSE
        ''', datetime.now() - timedelta(days=7))
        
        new_today = await conn.fetchval('''
            SELECT COUNT(*) FROM users 
            WHERE DATE(joined_at) = CURRENT_DATE
        ''')
        
        blocked_users = await conn.fetchval('SELECT COUNT(*) FROM users WHERE is_blocked = TRUE')
        
        return {
            'total': total_users or 0,
            'active': active_users or 0,
            'new_today': new_today or 0,
            'blocked': blocked_users or 0
        }

async def add_channel(channel_id: str, channel_name: str = None, invite_link: str = None):
    async with db.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO channels (channel_id, channel_name, invite_link)
            VALUES ($1, $2, $3)
            ON CONFLICT (channel_id) DO UPDATE SET channel_name = $2, invite_link = $3
        ''', channel_id, channel_name, invite_link)

async def remove_channel(channel_id: str):
    async with db.pool.acquire() as conn:
        await conn.execute('DELETE FROM channels WHERE channel_id = $1', channel_id)

async def get_all_channels():
    async with db.pool.acquire() as conn:
        return await conn.fetch('SELECT channel_id, channel_name, invite_link FROM channels')

async def save_broadcast(admin_id: int, message_text: str, sent_count: int, failed_count: int):
    async with db.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO broadcast_messages (admin_id, message_text, sent_count, failed_count)
            VALUES ($1, $2, $3, $4)
        ''', admin_id, message_text, sent_count, failed_count)
