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
            file = BufferedInputFile(data, filename or "media.bin")

            # Try sending as photo
            try:
                await message.answer_photo(file)
                return
            except TelegramBadRequest:
                pass

            # Try sending as video
            try:
                await message.answer_video(file)
                return
            except TelegramBadRequest:
                pass

            # Fallback: send as document
            await message.answer_document(file)