# That file provides all external functions for instagram part
import aiohttp
import asyncio


async def insta(url):
    api = f'https://backend1.tioo.eu.org/api/downloader/igdl?url={url}'

    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            data = await response.json()
            length = len(data)
            data = data[:int(length**(1/2))]
            print(len(data))
            return data

