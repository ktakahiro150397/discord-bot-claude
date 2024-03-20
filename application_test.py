import asyncio
import base64
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
from chatter.claude_token_calculator import ClaudeTokenCount
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

isDisplayTokenCount = True


async def test_text_stream(text_count:int):
    for i in range(text_count):
        if i % 30 == 0:
            yield f"{[i]}"
        else:
            yield f"{[i]}" + "```"



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

            # ファイル添付サイズ確認
            isExceed = False
            exceedFileName:list[str] = []
            for attachment in attachments:
                with open(attachment, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                
                    if len(encoded_string) > 5242880:
                        exceedFileName.append(attachment.name)
                        isExceed = True

            if isExceed:
                await message.channel.send(f"ファイルサイズが5MBを超えるため、送信できませんでした。\n\n{exceedFileName}")
                return

            # ストリーム版
            stream = test_text_stream(100)
            # stream = await chatters.chat_stream(message.channel.id,message.content,files=attachments)

            # ストリーム内容を送信
            (full_message,discordMessage) = await discord_helper.send_message_streaming(message.channel,stream,sendCount=5)

            # if isDisplayTokenCount:
            #     input_token = stream.current_message_snapshot.usage.input_tokens
            #     count = ClaudeTokenCount(input_token=input_token)
            #     input_token_doller = count.get_input_token_doller()
                
            #     output_token = await  count.output_token(chatters.clients[message.channel.id],full_message)
            #     output_token_doller = await count.get_output_token_doller(chatters.clients[message.channel.id],full_message)

            #     tokenInfo = f"[input token : {count.input_token} , :yen:{ input_token_doller * 150} / output token : {output_token} , :yen:{output_token_doller * 150} / sum : :yen:{(input_token_doller + output_token_doller) * 150}]"
            #     await discordMessage.edit(content=full_message + "\n" + tokenInfo)

            # await stream.close()
        except Exception as e:
            error_message = traceback.format_exc()
            
            logger.error(f"エラーが発生しました。\n{error_message}")
            await message.channel.send(f"エラーが発生しました。\n\n{error_message[-1800:]}")

    # 履歴を追加
    chatters.add_history(message.channel.id,role="assistant",message=full_message)


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


