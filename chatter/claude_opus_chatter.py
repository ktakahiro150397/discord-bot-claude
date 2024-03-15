
from pathlib import Path
from typing import List
from chatter.chat_interface import chat_interface


class claude_opus_chatter(chat_interface):
    def __init(self)->None:
        pass

    async def chat(self,id:str,message:str)->str:
        return f"chat called! / id:{id} / message : {message}"
    
    async def chat_stream(self,id:str,message:str,files:List[Path]=[])->None:
        return f"chat_stream called! / id:{id} / message : {message}"
    
    async def clear_history(self,id:str)->None:
        return f"clear_history called! / id:{id}"
    