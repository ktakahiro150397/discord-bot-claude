import asyncio
from datetime import datetime
import json
from logging import config, getLogger
from pathlib import Path
import sys
import traceback
from typing import Sequence
from discord import app_commands
import logging.handlers
import discord
from dotenv import load_dotenv
import os

from chatter.chat_interface import chat_interface
from chatter.claude_opus_chatter import ClaudeOpusChatter
from discord_helper import discord_helper

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

system_role = '''
あなたはAIアシスタント「くろーど・おーぱす」です。
10代の元気な美少女をイメージした口調で話してください。
'''

# チャットクラス
chatters = ClaudeOpusChatter(api_key=os.getenv("ANTHROPIC_API_KEY")
                             ,system_role=system_role)

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
            # # 同期版
            # response = await chatters.chat(message.channel.id,message.content)
            # await message.channel.send(f"{response}")

            # 添付ファイルあればダウンロード
            attachments:list[Path] = []
            
            for attachment in message.attachments:
                file_prefix = datetime.now().strftime("%Y%m%d%H%M%S")
                temp_file_path = f"user_upload_files/{file_prefix}_{attachment.filename}"
                file_path = await discord_helper.get_file_from_url(attachment.url,temp_file_path)
                attachments.append(file_path)
            

            # ストリーム版
            stream = await chatters.chat_stream(message.channel.id,message.content)

            # # ストリーム内容を送信
            # response = await discord_helper.send_message_streaming(message.channel,stream.text_stream,sendCount=10)

        except Exception as e:
            error_message = traceback.format_exc()
            
            logger.error(f"エラーが発生しました。\n{error_message}")
            await message.channel.send(f"エラーが発生しました。\n\n{error_message[-1800:]}")

    # # 履歴を追加
    # chatters.add_history(message.channel.id,role="assistant",message=response)


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
