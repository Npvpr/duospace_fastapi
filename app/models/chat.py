from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid

class ChatMessage(BaseModel):
    id: str
    text: str
    sender: str
    timestamp: str

    @classmethod
    def create(cls, text: str, sender: str = "Anonymous"):
        return cls(
            id=str(uuid.uuid4()),
            text=text,
            sender=sender,
            timestamp=datetime.now().isoformat()
        )