from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.database.queries import (
    get_stats, add_channel, remove_channel, 
    get_all_channels, get_all_users, save_broadcast, mark_user_blocked
)
from bot.keyboards.admin import (
    get_admin_menu, get_subscription_menu, 
    get_back_to_admin_button, get_cancel_button, get_channel_remove_keyboard
)

router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_channel_id = State()
    waiting_for_invite_link = State()

@router.callback_query(F.data == "admin_menu")
async def show_admin_menu(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await state.clear()
    
    await callback.message.edit_text(
        "👨‍💼 Admin Panel\n\nSelect an option:",
        reply_markup=get_admin_menu()
    )

@router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await state.clear()
    
    stats = await get_stats()
    
    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: {stats['total']}\n"
        f"✅ Active Users (7 days): {stats['active']}\n"
        f"🆕 New Users Today: {stats['new_today']}\n"
        f"🚫 Blocked Users: {stats['blocked']}"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_admin_button())

@router.callback_query(F.data == "admin_advertising")
async def start_advertising(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 <b>Advertising</b>\n\n"
        "Send me the message you want to broadcast to all users.\n"
        "You can send text, photo, video, or any other message type.",
        parse_mode="HTML",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext, is_admin: bool):
    if not is_admin:
        await message.answer("❌ You are not an admin!")
        return
    
    users = await get_all_users()
    
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await message.copy_to(user['user_id'])
            sent += 1
        except Exception:
            failed += 1
            await mark_user_blocked(user['user_id'])
    
    await save_broadcast(message.from_user.id, message.text or "Media message", sent, failed)
    
    await message.answer(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}",
        parse_mode="HTML",
        reply_markup=get_admin_menu()
    )
    await state.clear()

@router.callback_query(F.data == "admin_subscription")
async def subscription_management(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await state.clear()
    
    await callback.message.edit_text(
        "🔒 <b>Forced Subscription Management</b>\n\n"
        "Manage required channels for bot access:",
        parse_mode="HTML",
        reply_markup=get_subscription_menu()
    )

@router.callback_query(F.data == "sub_add_channel")
async def add_channel_start(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ <b>Add Channel</b>\n\n"
        "Send the channel ID or username (e.g., @channelusername or -1001234567890)",
        parse_mode="HTML",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_channel_id)

@router.message(AdminStates.waiting_for_channel_id)
async def process_add_channel(message: Message, state: FSMContext, is_admin: bool):
    if not is_admin:
        await message.answer("❌ You are not an admin!")
        return
    
    channel_id = message.text.strip()
    
    try:
        chat = await message.bot.get_chat(channel_id)
        
        if channel_id.startswith('@'):
            await add_channel(channel_id, chat.title)
            await message.answer(
                f"✅ Channel added successfully!\n\n"
                f"📢 {chat.title}",
                reply_markup=get_admin_menu()
            )
            await state.clear()
        else:
            await state.update_data(channel_id=channel_id, channel_name=chat.title)
            await message.answer(
                f"📢 Channel: {chat.title}\n\n"
                f"⚠️ This is a numeric/private channel ID.\n"
                f"Please send an invite link for users to join this channel.\n\n"
                f"You can create an invite link in the channel settings.",
                reply_markup=get_cancel_button()
            )
            await state.set_state(AdminStates.waiting_for_invite_link)
    except Exception as e:
        await message.answer(
            f"❌ Failed to add channel. Make sure:\n"
            f"1. The bot is an admin in the channel\n"
            f"2. The channel ID is correct\n\n"
            f"Error: {str(e)}",
            reply_markup=get_admin_menu()
        )
        await state.clear()

@router.callback_query(F.data == "sub_remove_channel")
async def remove_channel_menu(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await state.clear()
    
    channels = await get_all_channels()
    
    if not channels:
        await callback.message.edit_text(
            "📋 No channels added yet.",
            reply_markup=get_back_to_admin_button()
        )
        return
    
    await callback.message.edit_text(
        "❌ <b>Remove Channel</b>\n\nSelect a channel to remove:",
        parse_mode="HTML",
        reply_markup=get_channel_remove_keyboard(channels)
    )

@router.callback_query(F.data.startswith("remove_ch_"))
async def remove_channel_confirm(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await state.clear()
    
    channel_id = callback.data.replace("remove_ch_", "")
    await remove_channel(channel_id)
    
    await callback.message.edit_text(
        f"✅ Channel removed successfully!",
        reply_markup=get_admin_menu()
    )

@router.message(AdminStates.waiting_for_invite_link)
async def process_invite_link(message: Message, state: FSMContext, is_admin: bool):
    if not is_admin:
        await message.answer("❌ You are not an admin!")
        return
    
    invite_link = message.text.strip()
    
    if not (invite_link.startswith('https://t.me/') or invite_link.startswith('http://t.me/')):
        await message.answer(
            "❌ Invalid invite link format. It should start with https://t.me/\n\n"
            "Please send a valid invite link:",
            reply_markup=get_cancel_button()
        )
        return
    
    data = await state.get_data()
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')
    
    await add_channel(channel_id, channel_name, invite_link)
    await message.answer(
        f"✅ Channel added successfully!\n\n"
        f"📢 {channel_name}\n"
        f"🔗 Invite link: {invite_link}",
        reply_markup=get_admin_menu()
    )
    await state.clear()

@router.callback_query(F.data == "sub_list_channels")
async def list_channels(callback: CallbackQuery, state: FSMContext, is_admin: bool):
    await callback.answer()
    
    if not is_admin:
        await callback.answer("❌ You are not an admin!", show_alert=True)
        return
    
    await state.clear()
    
    channels = await get_all_channels()
    
    if not channels:
        await callback.message.edit_text(
            "📋 No channels added yet.",
            reply_markup=get_back_to_admin_button()
        )
        return
    
    text = "📋 <b>Required Channels:</b>\n\n"
    for i, channel in enumerate(channels, 1):
        channel_name = channel['channel_name'] or channel['channel_id']
        text += f"{i}. {channel_name}\n"
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_admin_button())
