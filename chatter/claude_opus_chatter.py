
from pathlib import Path
from typing import Dict, List
from chatter.chat_interface import chat_interface
import os
from anthropic import Anthropic

class claude_opus_chatter(chat_interface):
    def __init(self,apiKey:str)->None:
        self.clients:Dict[str,Anthropic] = {}

        self.apiKey = apiKey

    def add_client_before_process(f):
        def _wrapper(*args,**kwargs):
            print("add_client_before_process called!")

            v = f(*args,**kwargs)

            # print("add_client_before_process finished!")

            return v
        return _wrapper

    def __add_client(self,id:str)->None:
        if id not in self.clients:
            self.clients[id] = Anthropic(apiKey=self.apiKey)

    @add_client_before_process
    async def chat(self,id:str,message:str)->str:
        return f"chat called! / id:{id} / message : {message}"
    
    @add_client_before_process
    async def chat_stream(self,id:str,message:str,files:List[Path]=[])->None:
        return f"chat_stream called! / id:{id} / message : {message}"
    
    @add_client_before_process
    async def clear_history(self,id:str)->None:
        return f"clear_history called! / id:{id}"
    