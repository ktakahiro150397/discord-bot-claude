
from pathlib import Path
from typing import Dict, List
from chatter.chat_interface import chat_interface
import os
from anthropic import Anthropic

from chatter.claude_content import ClaudeContent

class ClaudeOpusChatter(chat_interface):
    def __init__(self,api_key:str,
                 model:str="claude-3-opus-20240229",
                 max_tokens:int=1024,
                 temperature:int=0,
                 system_role:str="")->None:
        self.clients:Dict[str,Anthropic] = {}
        self.contents:Dict[str,ClaudeContent] = {}
        
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.system_role = system_role


    def __add_client(self,memory_id:str)->None:
        if memory_id not in self.clients:
            self.clients[memory_id] = Anthropic(api_key=self.api_key)
        if memory_id not in self.contents:
            self.contents[memory_id] = ClaudeContent(items=[])

    async def chat(self,memory_id:str,message:str)->str:
        self.__add_client(memory_id)
        
        # メッセージ追加
        self.contents[memory_id].AddItem(role="user",content=message)
        
        # Claudeから返答を取得
        message = self.clients[memory_id].messages.create(
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            model=self.model,
            system=self.system_role,
            messages=self.contents[memory_id].GetSendMessage(),
        )
        
        # 返答を追加
        self.contents[memory_id].AddItem(role="assistant",content=message.content[0].text)
        
        return message.content[0].text
    
    async def chat_stream(self,memory_id:str,message:str,files:List[Path]=[])->None:
        self.__add_client(memory_id)
        return f"chat_stream called! / id:{memory_id} / message : {message}"
    
    async def clear_history(self,memory_id:str)->str:
        self.__add_client(memory_id)
        self.contents[memory_id].ClearItem()
        
        return "チャット履歴をクリアしました。"
    