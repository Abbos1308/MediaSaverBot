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


async def send_media(message, url: str, filename: str = None):
    """
    Fetch a file from URL and send it to Telegram as photo/video/document
    depending on content-type.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await message.answer("Failed to fetch media.")
                return

            data = await resp.read()
            content_type = resp.headers.get("Content-Type", "")

            # Decide how to send based on content-type
            if content_type.startswith("image"):
                await message.answer_photo(
                    BufferedInputFile(data, filename or "image.jpg")
                )
            elif content_type.startswith("video"):
                await message.answer_video(
                    BufferedInputFile(data, filename or "video.mp4")
                )
            else:
                await message.answer_document(
                    BufferedInputFile(data, filename or "file.bin")
                )