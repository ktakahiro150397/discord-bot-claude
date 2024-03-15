import asyncio
import json
from logging import config, getLogger
import sys
import traceback
from typing import Sequence
from discord import app_commands
import logging.handlers
import discord
from dotenv import load_dotenv
import os

from chatter.chat_interface import chat_interface
from chatter.claude_opus_chatter import claude_opus_chatter

# 環境変数を読み込み
load_dotenv()

# ログ設定読込
with open("logSettings.json") as f:
    config.dictConfig(json.load(f))
logger = getLogger(__name__)

# Discordクライアントのインスタンス化
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents,proxy=os.getenv("PROXY"))
tree = app_commands.CommandTree(client)

# discord側で反応するチャンネルのIDリスト。
responseChannelArray = os.getenv("DISCORD_RESPONSE_CHANNEL_ID").split(",")
responseChannel = [int(val) for val in responseChannelArray]
logger.info(f"反応対象のチャンネルIDは次の通りです。{responseChannel}")

# チャットクラス
chatters = claude_opus_chatter()

@client.event
async def on_ready():
    logger.debug(f"Called : {sys._getframe().f_code.co_name}")
    await tree.sync()
    logger.info(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    logger.debug(f"Called : {sys._getframe().f_code.co_name}")
    logger.debug(message)

    if message.channel.id not in responseChannel:
        logger.info(f"反応対象のチャンネルIDではありません。チャンネルID：{message.channel.id}")  
        return

    if message.author == client.user:
        logger.info("送信者が本人のため、何もしない")
        return
    
    if message.content.startswith("#"):
        logger.info("先頭が#のため、何もしない")
        return
    
    # ここで応答処理
    async with message.channel.typing():
        try:
            response = await chatters.chat(message.channel.id,message.content)
            await message.channel.send(f"{response}")
        except Exception as e:
            error_message = traceback.format_exc()
            
            logger.error(f"エラーが発生しました。\n{error_message}")
            await message.channel.send(f"エラーが発生しました。\n\n{error_message[-1800:]}")

@tree.command(name="clear",description="会話履歴をクリアします。")
async def clear_thread(interaction:discord.Interaction):
    await interaction.response.defer()

    logger.debug(f"Called : {sys._getframe().f_code.co_name}")
    logger.debug(f"interaction:{interaction}")

    response = await chatters.clear_history(interaction.channel.id)
    await interaction.followup.send(content=response)

# クライアントを実行
discord.utils.setup_logging()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
client.run(DISCORD_BOT_TOKEN)
