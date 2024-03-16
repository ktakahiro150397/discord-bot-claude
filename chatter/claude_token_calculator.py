from abc import ABC, abstractmethod
import base64
import dataclasses
import os
from pathlib import Path

from anthropic import AsyncAnthropic


@dataclasses.dataclass
class ClaudeTokenCount:
    input_token:int
    
    async def output_token(self,client:AsyncAnthropic,message:str)->int:
        return await client.count_tokens(message)
    
    def get_input_token_doller(self) -> float:
        return 15 * self.input_token / 1000000
    
    async def get_output_token_doller(self,client:AsyncAnthropic,message:str) -> float:
        output_token = await self.output_token(client,message)
        return 75 * output_token / 1000000
    