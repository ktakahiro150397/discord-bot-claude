import dataclasses


@dataclasses.dataclass
class ClaudeContentItem:
    role: str
    content: str
    
@dataclasses.dataclass
class ClaudeContent:
    items:list[ClaudeContentItem]
    
    def AddItem(self,role:str,content:str)->None:
        self.items.append(ClaudeContentItem(role=role,content=content))
        
    def GetSendMessage(self):
        return [
            {
                "role": item.role,
                "content": item.content
            } 
        for item in self.items
        ]
