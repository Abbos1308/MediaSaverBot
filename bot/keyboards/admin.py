from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📢 Advertising", callback_data="admin_advertising")],
        [InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔒 Forced Subscription", callback_data="admin_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_subscription_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Add Channel", callback_data="sub_add_channel")],
        [InlineKeyboardButton(text="❌ Remove Channel", callback_data="sub_remove_channel")],
        [InlineKeyboardButton(text="📋 List Channels", callback_data="sub_list_channels")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_admin_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="admin_menu")]
    ])

def get_cancel_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_menu")]
    ])

def get_channel_remove_keyboard(channels) -> InlineKeyboardMarkup:
    keyboard = []
    for channel in channels:
        channel_name = channel['channel_name'] or channel['channel_id']
        keyboard.append([InlineKeyboardButton(
            text=f"❌ {channel_name}", 
            callback_data=f"remove_ch_{channel['channel_id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
