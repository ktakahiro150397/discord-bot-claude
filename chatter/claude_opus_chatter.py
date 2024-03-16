
from pathlib import Path
from typing import Dict, List
from chatter.chat_interface import chat_interface
import os
from anthropic import Anthropic

class claude_opus_chatter(chat_interface):
    def __init__(self,api_key:str)->None:
        self.clients:Dict[str,Anthropic] = {}

        self.api_key = api_key

    def __add_client(self,id:str)->None:
        if id not in self.clients:
            self.clients[id] = Anthropic(api_key=self.api_key)

    async def chat(self,id:str,message:str)->str:
        self.__add_client(id)
        return f"chat called! / id:{id} / message : {message}"
    
    async def chat_stream(self,id:str,message:str,files:List[Path]=[])->None:
        self.__add_client(id)
        return f"chat_stream called! / id:{id} / message : {message}"
    
    async def clear_history(self,id:str)->None:
        self.__add_client(id)
        return f"clear_history called! / id:{id}"
    