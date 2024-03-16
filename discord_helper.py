from pathlib import Path
from typing import AsyncIterator

import aiohttp
import discord


class discord_helper:

    async def send_message_streaming(message_channel:discord.TextChannel,
                                     stream:AsyncIterator[str],
                                     sendCount:int=10) -> str:
        

        hasFirstMessageSend = False
        discordMessage = None

        full_message = ""

        currentCount:int = 0
        async for message in stream:
            currentCount += 1
            full_message += message

            if currentCount >= sendCount:
                currentCount = 0
                if not hasFirstMessageSend:
                    discordMessage = await message_channel.send(full_message)
                    hasFirstMessageSend = True
                else:
                    await discordMessage.edit(content=full_message)

        full_message += "\n:white_check_mark:"
        if not hasFirstMessageSend:
            discordMessage = await message_channel.send(full_message)
            hasFirstMessageSend = True
        else:
            await discordMessage.edit(content=full_message)

        return full_message

    async def get_file_from_url(url:str,temp_file_path:str) -> Path:
        # ファイルをダウンロード
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"GET {url} failed with status {resp.status}")
                data = await resp.read()
                with open(temp_file_path, "wb") as f:
                    f.write(data)

        return Path(temp_file_path)