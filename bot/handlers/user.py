from aiogram import Router, F , Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.queries import add_user, update_user_activity
from bot.utils.helpers import check_user_subscription
from bot.keyboards.user import get_subscription_check_keyboard , ytformatskeyboard
from bot.keyboards.admin import get_admin_menu
from functions.insta import insta , send_media
from functions.yt import yt
import json

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
            "⚠️ Botdan foydalanish uchun avval quyidagi kanallarga a'zo bo'lishingiz zarur:",
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
            f"👋 Assalomu alaykum, {user.first_name}!\n\n"
            "Ishni boshlashim uchun havolani yuboring 🖇️\n\n"
            "Qo'llab quvvatlanadigan ijtimoiy tarmoqlar: \n"
            "• Instagram\n"
            "• YouTube\n\n"
            "Tez orada boshqa ijtimoiy tarmoq funksiyalari ham qo'shiladi. Kuzatib boring"
        )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, is_admin: bool):
    await callback.answer()
    
    user = callback.from_user
    await update_user_activity(user.id)
    
    is_subscribed, not_subscribed_channels = await check_user_subscription(callback.bot, user.id)
    
    if not is_subscribed:
        await callback.message.edit_text(
            "❌ Barcha kanallarga a'zo bo'lmagansiz! Qayta urunib ko'ring.",
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

@router.callback_query(F.data.contains("yt"))
async def download_yt(callback: CallbackQuery, bot: Bot):
    await callback.answer()

    # Parse callback_data back to dict
    payload = json.loads(callback.data)
    fmt = payload["format"].lower().replace("🎵 ", "").replace("🎥 ", "")

    url = payload["url"]

    temp_msg = await callback.message.answer("⏳")

    quality = None
    if fmt != "mp3":
        quality = fmt.replace("🎥 ", "")  # extract number like 360/720
        fmt = "mp4"

    data = await yt(url, fmt, quality=quality)

    # Delete temp message
    await bot.deletemessage(chatid=callback.message.chat.id, messageid=tempmsg.message_id)

    if data.get("status"):
        if fmt == "mp3":
            await callback.message.answer_audio(data["download"]["url"])
        else:
            await callback.message.answer_video(data["download"]["url"])
    else:
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko`ring.")

@router.message(lambda msg: msg.text.startswith("https://www.instagram"))
async def instagram_handler(message: Message,bot:Bot):
    temp_msg = await message.answer("⏳")
    url = message.text
    files = await insta(url)
    await bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
    for i in files:
        await send_media(message,i['url'])

@router.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def ytfetchhandler(message: Message, bot: Bot):
    url = message.text
    #print("working...")
    metadata = await yt(url)
    thumbnail = metadata["thumbnails"][2]["url"]
    print(thumbnail)
    title = metadata["title"]

    await message.answer_photo(
        thumbnail,
        caption=title,
        reply_markup=ytformatskeyboard(url, ["🎵 Mp3", "🎥 360", "🎥 720"])
   )