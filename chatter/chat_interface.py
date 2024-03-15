from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

class chat_interface(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def chat(self,id:str,message:str)->str:
        return "got message! : {message}"
    
    @abstractmethod
    async def chat_stream(self,id:str,message:str,files:List[Path]=[])->None:
        pass

    @abstractmethod
    async def clear_history(self,id:str)->None:
        pass
    