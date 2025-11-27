from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscription_check_keyboard(channels) -> InlineKeyboardMarkup:
    keyboard = []
    
    for channel in channels:
        channel_id = channel['channel_id']
        channel_name = channel['channel_name'] or channel_id
        invite_link = channel.get('invite_link')
        
        if channel_id.startswith('@'):
            url = f"https://t.me/{channel_id.replace('@', '')}"
            keyboard.append([InlineKeyboardButton(
                text=f"📢 {channel_name}", 
                url=url
            )])
        elif invite_link:
            keyboard.append([InlineKeyboardButton(
                text=f"📢 {channel_name}", 
                url=invite_link
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                text=f"📢 {channel_name} (no link available)", 
                callback_data="no_action"
            )])
    
    keyboard.append([InlineKeyboardButton(text="✅ Check Subscription", callback_data="check_subscription")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def ytformatskeyboard(url: str, formats: list[str]) -> InlineKeyboardMarkup:
    keyboard = []
    for fmt in formats:
        payload = {"type": "yt", "format": fmt, "url": url}
        keyboard.append([
            InlineKeyboardButton(
                text=fmt,
                callback_data=json.dumps(payload)  # must be string
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)