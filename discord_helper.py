from pathlib import Path
from typing import AsyncIterator

import aiohttp
import discord
from discord import Message


class discord_helper:

    async def send_message_streaming(message_channel:discord.TextChannel,
                                     stream:AsyncIterator[str],
                                     sendCount:int=10,
                                     characterCount:int=1800):
        

        hasFirstMessageSend = False
        discordMessage = None

        full_message = ""
        current_message = ""
        sent_message = ""

        currentCount:int = 0
        async for message in stream:
            currentCount += 1

            if len(current_message) > characterCount:
                # しきい値を超えている場合、新しいメッセージとする
                hasFirstMessageSend = False
                current_message = current_message.replace(sent_message,"")

            full_message += message
            current_message += message

            if currentCount >= sendCount:
                currentCount = 0
                if not hasFirstMessageSend:
                    discordMessage = await message_channel.send(current_message)
                    hasFirstMessageSend = True
                    sent_message = current_message
                else:
                    markdown_count = current_message.count("```")
                    if markdown_count % 2 == 0:
                        await discordMessage.edit(content=current_message)
                    else:
                        await discordMessage.edit(content=current_message + "```")
                    
                    sent_message = current_message

        current_message += "\n:white_check_mark:"
        if not hasFirstMessageSend:
            discordMessage = await message_channel.send(current_message)
            hasFirstMessageSend = True
        else:
            await discordMessage.edit(content=current_message)

        return (full_message,discordMessage)

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