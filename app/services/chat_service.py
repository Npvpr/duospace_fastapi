from typing import List
from app.models.chat import ChatMessage

class ChatService:
    def __init__(self):
        self._chat_history: List[ChatMessage] = []

    def add_message(self, message: ChatMessage) -> ChatMessage:
        self._chat_history.append(message)
        return message

    def get_message_history(self) -> List[ChatMessage]:
        return self._chat_history.copy()  # Return copy to prevent external modification

    def get_recent_messages(self, count: int = 50) -> List[ChatMessage]:
        return self._chat_history[-count:]

    def clear_history(self):
        self._chat_history.clear()

# Create a singleton instance
chat_service = ChatService()