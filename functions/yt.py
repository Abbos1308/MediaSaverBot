# That file provides all external functions for YouTube part
import aiohttp
import asyncio


async def yt(url, format="metadata", quality=360):
    api_domain = "https://ytapi-4yz7.onrender.com/"
    if format == "metadata":
        api = f"{api_domain}metadata?url={url}"
    elif format == "mp3":
        api = f"{api_domain}mp3?url={url}"
    elif format == "mp4":
        api = f"{api_domain}mp4?url={url}&quality={quality}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            return await response.json()


print(asyncio.run(yt("https://youtu.be/KRedCn1d0Ys?si=8X6Vij7a-0xOdsD5",format="mp3")))
