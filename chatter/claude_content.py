from abc import ABC, abstractmethod
import base64
import dataclasses
import os
from pathlib import Path




class ClaudeContentItemBase(ABC):
    role:str

    @abstractmethod
    def to_dict(self):
        pass


@dataclasses.dataclass
class ClaudeContentTextItem(ClaudeContentItemBase):
    text: str
    
    def to_dict(self):
        return {
            "type": "text",
            "text": self.text
        }

@dataclasses.dataclass
class ClaudeContentImageItem(ClaudeContentItemBase):
    file_name:Path

    def to_dict(self):
        file_extension = self.file_name.suffix.replace(".", "")
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{file_extension}",
                "data": self.encode_image_to_base64()
            }
        }
    
    def encode_image_to_base64(self):
        with open(self.file_name, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string
    
@dataclasses.dataclass
class ClaudeContentMessageElement:
    role: str
    content: list[ClaudeContentItemBase]

@dataclasses.dataclass
class ClaudeContent:
    items:list[ClaudeContentMessageElement]

    def AddContent(self,role:str,text:str,file_name_list:list[Path]=[])->None:
        addItem = ClaudeContentMessageElement(role=role,content=[])

        if text != "":
            addItem.content.append(ClaudeContentTextItem(text=text))

        for file in file_name_list:
            addItem.content.append(ClaudeContentImageItem(file_name=file))
        
        self.items.append(addItem)
    
    # def AddTextContent(self,role:str,content:str)->None:
    #     self.items.append(ClaudeContentTextItem(role=role,text=content))

    # def AddImageContent(self,role:str,file_name:Path)->None:
    #     self.items.append(ClaudeContentImageItem(role=role,file_name=file_name))
        
    def ClearItem(self)->None:
        self.items = []    
    
    def GetSendMessage(self):
        return [
            {
                "role": item.role,
                "content": [content.to_dict() for content in item.content]
            }
        for item in self.items
        ]
