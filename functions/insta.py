# That file provides all external functions for instagram part
import aiohttp
import asyncio
from aiogram.types import BufferedInputFile


async def insta(url):
    api = f'https://backend1.tioo.eu.org/api/downloader/igdl?url={url}'

    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            data = await response.json()
            length = len(data)
            data = data[:int(length**(1/2))]
            print(len(data))
            return data

import aiohttp
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

async def send_media(message, url: str, filename: str = None):
    """
    Fetch a file from URL and send it inline as photo/video if possible.
    Falls back to document if neither works.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await message.answer("Failed to fetch media.")
                return
            

            data = await resp.read()
            if resp.headers.get("Content-Disposition").endswith(".jpg"):
                filename = "picture.jpg"
            elif resp.headers.get("Content-Disposition").endswith(".mp4"):
                filename = "video.mp4"
            else :
                await message.answer("Fayl formati qo'llab quvvatlanmaydi. Iltimos havolani tekshirib qayta yuboring.")
            file = BufferedInputFile(data, filename)

            # Try sending as photo
            if filename=="picture.jpg":
                await message.answer_photo(file)
                return

            # Try sending as video
            elif filename=="video.mp4":
                await message.answer_video(file)
                return

            # Fallback: send as document
            await message.answer_document(file)