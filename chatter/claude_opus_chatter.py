
from pathlib import Path
from typing import Dict, List
from chatter.chat_interface import chat_interface
import os
from anthropic import AsyncAnthropic, AsyncMessageStream

from chatter.claude_content import ClaudeContent

class ClaudeOpusChatter(chat_interface):
    def __init__(self,api_key:str,
                 model:str="claude-3-opus-20240229",
                 max_tokens:int=1024,
                 temperature:int=0,
                 system_role:str="")->None:
        self.clients:Dict[str,AsyncAnthropic] = {}
        self.contents:Dict[str,ClaudeContent] = {}
        
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.system_role = system_role


    def __add_client(self,memory_id:str)->None:
        if memory_id not in self.clients:
            self.clients[memory_id] = AsyncAnthropic(api_key=self.api_key)
        if memory_id not in self.contents:
            self.contents[memory_id] = ClaudeContent(items=[])

    async def chat(self,memory_id:str,message:str)->str:
        self.__add_client(memory_id)
        
        # メッセージ追加
        self.contents[memory_id].AddItem(role="user",content=message)
        
        # Claudeから返答を取得
        message = await self.clients[memory_id].messages.create(
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            model=self.model,
            system=self.system_role,
            messages=self.contents[memory_id].GetSendMessage(),
        )
        
        # 返答を追加
        self.contents[memory_id].AddItem(role="assistant",content=message.content[0].text)
        
        return message.content[0].text
    
    async def chat_stream(self,memory_id:str,message:str,files:List[Path]=[])->AsyncMessageStream:
        self.__add_client(memory_id)

        # メッセージ追加
        self.contents[memory_id].AddItem(role="user",content=message)

        # response_message = ""
        # async with self.clients[memory_id].messages.stream(
        #         max_tokens=self.max_tokens,
        #         temperature=self.temperature,
        #         messages=self.contents[memory_id].GetSendMessage(),
        #         model="claude-3-opus-20240229",
        #     ) as stream:
        #         async for text in stream.text_stream:
        #             print(text, end="", flush=True)
        #         print()

        #         response_message = await stream.get_final_message()
        #         print(response_message.model_dump_json(indent=2))

        # self.contents[memory_id].AddItem(role="assistant",content=response_message)

        stream = await self.clients[memory_id].messages.stream(
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=self.contents[memory_id].GetSendMessage(),
            model="claude-3-opus-20240229",
            system=self.system_role,
        ).__aenter__()

        return stream
    
    def add_history(self,memory_id:str,role:str,message:str)->None:
        self.__add_client(memory_id)
        self.contents[memory_id].AddItem(role=role,content=message)
    
    async def clear_history(self,memory_id:str)->str:
        self.__add_client(memory_id)
        self.contents[memory_id].ClearItem()
        
        return "チャット履歴をクリアしました。"
    