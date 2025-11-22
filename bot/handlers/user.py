from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.queries import add_user, update_user_activity
from bot.utils.helpers import check_user_subscription
from bot.keyboards.user import get_subscription_check_keyboard
from bot.keyboards.admin import get_admin_menu
from functions.insta import insta,  send_media


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, is_admin: bool):
    user = message.from_user
    await add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    is_subscribed, not_subscribed_channels = await check_user_subscription(message.bot, user.id)
    
    if not is_subscribed:
        await message.answer(
            "⚠️ To use this bot, you must subscribe to the following channels:",
            reply_markup=get_subscription_check_keyboard(not_subscribed_channels)
        )
        return
    
    if is_admin:
        await message.answer(
            f"👋 Welcome, Admin {user.first_name}!\n\n"
            "Use the menu below to access admin panel:",
            reply_markup=get_admin_menu()
        )
    else:
        await message.answer(
            f"👋 Welcome, {user.first_name}!\n\n"
            "You have access to the bot. Use /start to see this message again."
        )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, is_admin: bool):
    await callback.answer()
    
    user = callback.from_user
    await update_user_activity(user.id)
    
    is_subscribed, not_subscribed_channels = await check_user_subscription(callback.bot, user.id)
    
    if not is_subscribed:
        await callback.message.edit_text(
            "❌ You are still not subscribed to all required channels!",
            reply_markup=get_subscription_check_keyboard(not_subscribed_channels)
        )
        return
    
    await callback.message.delete()
    
    if is_admin:
        await callback.message.answer(
            f"✅ Subscription verified!\n\n"
            f"👋 Welcome, Admin {user.first_name}!",
            reply_markup=get_admin_menu()
        )
    else:
        await callback.message.answer(
            f"✅ Subscription verified!\n\n"
            f"👋 Welcome, {user.first_name}!"
        )


@router.message(lambda msg: msg.text.startswith("https://www.instagram"))
async def instagram_handler(message: Message):
    url = message.text
    files = await insta(url)
    for i in files:
        await send_media(message,i['url'])